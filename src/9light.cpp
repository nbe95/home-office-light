#include <BridgeClient.h>
#include <BridgeHttpClient.h>
#include <BridgeServer.h>
#include <Adafruit_NeoPixel.h>
#include "9light.h"
#include "map.h"
#include "timer.h"
#include "animation.h"
#include "helpers.h"

#define HTTP_READ_TIMEOUT 10

NineLightRemote::NineLightRemote(const api_config* const api_config, const led_config* const led_config):
    m_api_config(api_config),
    m_led_config(led_config),
    m_pixels(new Adafruit_NeoPixel(led_config->num_leds, (uint16_t)led_config->do_pin, led_config->options))
{
    m_pixels->begin();
}


BridgeServer* NineLightRemote::getHttpServer()
{
    if (!m_http_server)
    {
        m_http_server = new BridgeServer(m_api_config->remote_port);
        m_http_server->noListenOnLocalhost();
        m_http_server->begin();
    }
    return m_http_server;
}


BridgeHttpClient* NineLightRemote::getHttpClient()
{
    if (!m_http_client)
    {
        m_http_client = new BridgeHttpClient();
        m_http_client->setTimeout(HTTP_READ_TIMEOUT);
    }
    return m_http_client;
}


bool NineLightRemote::registerButton(const state target_state, const pin button_pin, const bool int_pullup)
{
    if (button_pin == 0)
        return false;

    m_button_map.add(target_state, button_pin);
    pinMode(button_pin, (int_pullup ? INPUT_PULLUP : INPUT));

    return true;
}


void NineLightRemote::setButtonTimeout(const Timer::ms timeout)
{
    m_button_timer.setDuration(timeout);
}


void NineLightRemote::updateLeds()
{
    // LED state machine
    if (m_leds_state != m_state)
    {
        // Clear old animation
        delete m_animation;
        m_animation = 0;

        // Setup new animation object
        m_leds_state = m_state;
        switch (m_leds_state)
        {
            case state::CALL:
            {
                WaveAnimation* ptr = new WaveAnimation();
                ptr->setBaseColor(Animation::rgb(255, 150, 0));
                ptr->setPeriod(2500);
                ptr->setMinMax(40, 255);
                m_animation = ptr;
                break;
            }
            case state::VIDEO:
            {
                WaveAnimation* ptr = new WaveAnimation();
                ptr->setBaseColor(Animation::rgb(255, 0, 0));
                ptr->setPeriod(2500);
                ptr->setMinMax(40, 255);
                m_animation = ptr;
                break;
            }
            case state::REQUEST:
            {
                WaveAnimation* ptr = new WaveAnimation();
                ptr->setBaseColor(Animation::rgb(0, 200, 255));
                ptr->setPeriod(300);
                ptr->setMinMax(0, 255);
                m_animation = ptr;
                break;
            }
            case state::COFFEE:
            {
                WaveAnimation* ptr = new WaveAnimation();
                ptr->setBaseColor(Animation::rgb(0, 255, 0));
                ptr->setPeriod(100);
                ptr->setMinMax(0, 255);
                m_animation = ptr;
                break;
            }
            case state::NONE:
            default:
            {
                break;
            }
        }
    }

    //// On/off animation
    //if (m_leds_state == state::REQUEST)
    //{
        //// Full period expired?
        //if (m_leds_timer.check())
        //{
            //m_leds_timer.restart();
            //if (m_leds_state == state::COFFEE)
                //m_leds_color = random(0xFFFFFF);
        //}
        //// Half period expired?
        //else if (m_leds_timer.getElapsedTime() >= m_leds_timer.getDuration() / 2)
        //{
            //m_leds_color = 0;
        //}
    //}

    Animation::color col = 0;
    if (m_animation)
        col = m_animation->getColor();
    m_pixels->fill(col);
    m_pixels->show();
}


void NineLightRemote::pollButtons()
{
    m_button_timer.start();
    if (!m_button_timer.check())
        return;

    state button = state::UNDEFINED;
    pin di_pin = 0;
    for (int i = 0; i < m_button_map.size(); i++)
    {
        m_button_map.getKey(i, &button);
        m_button_map.getValue(button, &di_pin);

        if (di_pin != 0 && digitalRead(di_pin) == LOW)
        {
            sendStateRequest(button);
            m_button_timer.restart();
            return;
        }
    }
}


void NineLightRemote::pollRemoteRequest()
{
    BridgeClient client = getHttpServer()->accept();
    if (client)
    {
        // Find beginning of JSON payload (i.e. line starting with '{')
        char request[80] = {0};
        size_t bytes;
        client.setTimeout(HTTP_READ_TIMEOUT);
        do
        {
            memset(request, 0, sizeof(request));
            bytes = client.readBytesUntil('\n', request, sizeof(request));
            SerialUSB.println(request);
            if (bytes == 0)
                break;
        } while (request[0] != '{');
        client.flush();
        client.print(F("HTTP/1.1 200 OK\n"));

        SerialUSB.print(F("Incoming HTTP request: "));
        SerialUSB.println(request);

        state result = parseJsonState(request);
        if (result != state::UNDEFINED)
            setState(result);
    }
    client.stop();
}


void NineLightRemote::sendStateRequest(const state state_req)
{
    char query[80] = {0};
    char state_str[10] = "undefined";
    stateToCStr(state_req, state_str);

    sprintf(query, "%s:%d%s/set?status=%s&remote", m_api_config->endpoint, m_api_config->port, m_api_config->url, state_str);
    SerialUSB.print(F("Sending HTTP request to: "));
    SerialUSB.println(query);

    getHttpClient()->get(query);

    char response[80] = {0};
    if (getHttpClient()->available())
    {
        getHttpClient()->readBytesUntil('\n', response, sizeof(response) - 1);
        SerialUSB.print(F("Got response: "));
        SerialUSB.println(response);

        state result = parseJsonState(response);
        if (result != state::UNDEFINED)
            setState(result);
    }
}


bool NineLightRemote::stateToCStr(const state state, char* target)
{
    switch (state)
    {
        case state::NONE:
            strcpy(target, "none");
            return true;
        case state::CALL:
            strcpy(target, "call");
            return true;
        case state::VIDEO:
            strcpy(target, "video");
            return true;
        case state::REQUEST:
            strcpy(target, "request");
            return true;
        case state::COFFEE:
            strcpy(target, "coffee");
            return true;
    }
    return false;
}


NineLightRemote::state NineLightRemote::stateFromCStr(const char* buffer)
{
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


NineLightRemote::state NineLightRemote::parseJsonState(const char* buffer)
{
    // Look for JSON key
    const char key[] = "\"status\":";
    char *ptr = strstr(buffer, key);
    if (ptr == 0)
        return state::UNDEFINED;

    // Skip any spaces
    ptr += strlen(key);
    while (*ptr++ == ' ') ;

    return stateFromCStr(ptr);
}