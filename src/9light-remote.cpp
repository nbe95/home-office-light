// Copyright (c) 2022 Niklas Bettgen

#include "9light-remote.h"

#define HTTP_READ_TIMEOUT 10


NineLightRemote::NineLightRemote(const api_config* const api_config, const led_config* const led_config) :
m_api_config(api_config),
m_led_config(led_config),
m_pixels(new Adafruit_NeoPixel(led_config->num_leds, led_config->do_pin.getPin(), led_config->options)),
m_button_map(4, NineLightRemote::state::UNDEFINED, nullptr) {
    m_pixels->begin();
}


NineLightRemote::~NineLightRemote() {
    delete m_pixels;
    delete m_http_server;
    delete m_http_client;
    for (ButtonMap::iter it = m_button_map.begin(); it < m_button_map.end(); it++) {
        if (it->value != nullptr)
            delete it->value;
    }
}


BridgeServer* NineLightRemote::getHttpServer() {
    if (!m_http_server) {
        m_http_server = new BridgeServer(m_api_config->remote_port);
        m_http_server->noListenOnLocalhost();
        m_http_server->begin();
    }
    return m_http_server;
}


BridgeHttpClient* NineLightRemote::getHttpClient() {
    if (!m_http_client) {
        m_http_client = new BridgeHttpClient();
        m_http_client->setTimeout(HTTP_READ_TIMEOUT);
    }
    return m_http_client;
}


bool NineLightRemote::registerButton(const state target_state, const Pin button_pin, const Timer::ms debounce_time) {
    if (!button_pin.isValid())
        return false;

    button_pin.setup();
    DebouncedSwitch* button = new DebouncedSwitch(button_pin, debounce_time);
    m_button_map.set(target_state, button);

    return true;
}


void NineLightRemote::setupIdleRequest(const Timer::ms interval) {
    m_idle_timer.setDuration(interval);
}


void NineLightRemote::updateLeds() {
    // LED state machine
    if (m_leds_state != m_state) {
        // Clear old animation
        delete m_animation;
        m_animation = nullptr;

        // Setup new animation object
        m_leds_state = m_state;
        switch (m_leds_state) {
            case state::CALL: {
                WaveAnimation* ptr = new WaveAnimation(2500);
                ptr->setBaseColor(Animation::RGB(255, 150, 0));
                ptr->setMinMax(40, 255);
                m_animation = ptr;
                break;
            }
            case state::VIDEO: {
                WaveAnimation* ptr = new WaveAnimation(2500);
                ptr->setBaseColor(Animation::RGB(255, 0, 0));
                ptr->setMinMax(40, 255);
                m_animation = ptr;
                break;
            }
            case state::REQUEST: {
                OnOffAnimation* ptr = new OnOffAnimation(200, 150);
                ptr->setBaseColor(Animation::RGB(0, 200, 255));
                m_animation = ptr;
                break;
            }
            case state::COFFEE: {
                RainbowAnimation* ptr = new RainbowAnimation(600);
                m_animation = ptr;
                break;
            }
            case state::NONE:
            default: {
                break;
            }
        }
    }

    Animation::color col = 0;
    if (m_animation)
        col = m_animation->getColor();
    m_pixels->fill(col);
    m_pixels->show();
}


void NineLightRemote::pollButtons() {
    for (ButtonMap::iter it = m_button_map.begin(); it < m_button_map.end(); it++) {
        DebouncedSwitch* button = it->value;
        if (button != nullptr) {
            button->debounce();
            if (button->hasChanged() && button->isClosed()) {
                SerialUSB.println(F("Button pressed."));
                sendStateRequest(it->key);
            }
        }
    }
}


void NineLightRemote::receiveRemoteRequest() {
    BridgeClient client = getHttpServer()->accept();
    if (client) {
        // Find beginning of JSON payload (i.e. line starting with '{')
        // Note: The entire JSON content must be sent as one-line string!
        char request[80];
        size_t bytes;
        client.setTimeout(HTTP_READ_TIMEOUT);
        do {
            memset(request, 0, sizeof(request));
            bytes = client.readBytesUntil('\n', request, sizeof(request));
        } while (request[0] != '{');
        client.flush();
        client.print(F("HTTP/1.1 200 OK\n"));

        SerialUSB.print(F("Incoming HTTP request: "));
        SerialUSB.println(request);

        state result = ParseJsonState(request);
        if (result != state::UNDEFINED)
            setState(result);
    }
    client.stop();
}


void NineLightRemote::sendRequestIfIdle() {
    if (!m_idle_timer.isSet())
        return;

    m_idle_timer.start();
    if (m_idle_timer.checkAndRestart()) {
        SerialUSB.println(F("Time for a cyclic state request in order to keep the remote registration state."));
        sendStateRequest();
    }
}


// Will set the 9Light state if state_req is set, otherwise will only get the current state.
void NineLightRemote::sendStateRequest(const state state_req) {
    char query[80] = {0};
    if (state_req != state::UNDEFINED) {
        char state_str[10] = "undefined";
        StateToCStr(state_req, state_str);
        sprintf_P(query, PSTR("%s:%d%s?state=%s&remote"), m_api_config->endpoint, m_api_config->port, m_api_config->uri_set, state_str);
    } else {
        sprintf_P(query, PSTR("%s:%d%s?remote"), m_api_config->endpoint, m_api_config->port, m_api_config->uri_get);
    }
    SerialUSB.print(F("Sending HTTP request to: "));
    SerialUSB.println(query);

    getHttpClient()->get(query);

    char response[80] = {0};
    if (getHttpClient()->available()) {
        getHttpClient()->readBytesUntil('\n', response, sizeof(response));
        SerialUSB.print(F("Got response: "));
        SerialUSB.println(response);

        state result = ParseJsonState(response);
        if (result != state::UNDEFINED)
            setState(result);
    }

    m_idle_timer.restart();
}


bool NineLightRemote::StateToCStr(const state state, char* const target) {
    switch (state) {
        case state::NONE:
            sprintf_P(target, PSTR("none"));
            return true;
        case state::CALL:
            sprintf_P(target, PSTR("call"));
            return true;
        case state::VIDEO:
            sprintf_P(target, PSTR("video"));
            return true;
        case state::REQUEST:
            sprintf_P(target, PSTR("request"));
            return true;
        case state::COFFEE:
            sprintf_P(target, PSTR("coffee"));
            return true;
    }
    return false;
}


NineLightRemote::state NineLightRemote::StateFromCStr(const char* const buffer) {
    const char status_none[]    = "none";
    const char status_call[]    = "call";
    const char status_video[]   = "video";
    const char status_request[] = "request";
    const char status_coffee[]  = "coffee";

    if (memcmp(buffer, status_none, strlen(status_none)) == 0)
        return state::NONE;
    if (memcmp(buffer, status_call, strlen(status_call)) == 0)
        return state::CALL;
    if (memcmp(buffer, status_video, strlen(status_video)) == 0)
        return state::VIDEO;
    if (memcmp(buffer, status_request, strlen(status_request)) == 0)
        return state::REQUEST;
    if (memcmp(buffer, status_coffee, strlen(status_coffee)) == 0)
        return state::COFFEE;

    return state::UNDEFINED;
}


NineLightRemote::state NineLightRemote::ParseJsonState(const char* const buffer) {
    // Look for JSON key
    const char key[] = "\"state\":";
    char *ptr = strstr(buffer, key);
    if (ptr == nullptr)
        return state::UNDEFINED;

    // Skip any spaces
    ptr += strlen(key);
    while (*ptr++ == ' ') {}

    return StateFromCStr(ptr);
}
