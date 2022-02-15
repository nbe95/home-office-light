// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_9LIGHT_REMOTE_H_
#define SRC_9LIGHT_REMOTE_H_

#include <BridgeClient.h>
#include <BridgeHttpClient.h>
#include <BridgeServer.h>
#include <Adafruit_NeoPixel.h>
#include "./map.h"
#include "./timer.h"
#include "./debouncer.h"
#include "./animation.h"
#include "./helpers.h"


class NineLightRemote {
 public:
    // Type definitions
    enum state { UNDEFINED = 0, NONE, CALL, VIDEO, REQUEST, COFFEE };
    struct api_config {
        const char*     endpoint;
        const char*     url;
        unsigned int    port;
        unsigned int    remote_port;
    };
    struct led_config {
        Pin         do_pin;
        uint16_t    num_leds;
        uint16_t    options;
    };

    // Constructor and destructor
    NineLightRemote(const api_config* const api_config, const led_config* const led_config);
    ~NineLightRemote();

    // General methods
    void                setState(const state state) { m_state = state; }
    state               getState() const { return m_state; }

    // Setup
    bool                registerButton(const state target_state, const Pin button_pin, const Timer::ms debounce_time);
    void                setupIdleRequest(const Timer::ms interval);

    // Cylic routines
    void                receiveRemoteRequest();
    void                sendRequestIfIdle();
    void                pollButtons();
    void                updateLeds();

    // 9Light interface methods
    void                sendStateRequest(const state state = state::UNDEFINED);

 private:
    // Static helper functions
    static bool         StateToCStr(const state state, char* target);
    static state        StateFromCStr(const char* buffer);
    static state        ParseJsonState(const char* buffer);

    BridgeServer*       getHttpServer();
    BridgeHttpClient*   getHttpClient();


    // Configuration
    const api_config*   m_api_config;
    const led_config*   m_led_config;

    // Hardware buttons
    using ButtonMap = StaticMap<state, DebouncedSwitch*, 4>;
    ButtonMap           m_button_map;

    // Internal status
    state               m_state = state::UNDEFINED;
    Timer               m_idle_timer;

    // LED status
    Adafruit_NeoPixel*  m_pixels;
    state               m_leds_state = state::UNDEFINED;
    Animation*          m_animation;

    // 9Light server and client
    BridgeHttpClient*   m_http_client;
    BridgeServer*       m_http_server;
};

#endif  // SRC_9LIGHT_REMOTE_H_
