#ifndef _9LIGHT_H_
#define _9LIGHT_H_

#include <BridgeClient.h>
#include <BridgeHttpClient.h>
#include <BridgeServer.h>
#include <Adafruit_NeoPixel.h>
#include <avr/power.h>
#include "map.h"
#include "timer.h"
#include "animation.h"
#include "helpers.h"


class NineLightRemote
{
public:
    // Type definitions
    enum state {
        UNDEFINED,
        NONE,
        CALL,
        VIDEO,
        REQUEST,
        COFFEE
    };
    struct api_config {
        const char*     endpoint;
        const char*     url;
        unsigned int    port;
        unsigned int    remote_port;
    };
    struct led_config {
        pin         do_pin;
        uint16_t    num_leds;
        uint16_t    options;
    };
    //struct button_map
        //state   button;
        //pin     di_pin;
    //};

    // Constructor and destructor
    NineLightRemote(const api_config* const api_config, const led_config* const led_config);

    // General methods
    void                setState(const state state) { m_state = state; };
    state               getState() const { return m_state; };

    // Setup
    bool                registerButton(const state state, const pin pin, const bool int_pullup = true);
    void                setButtonTimeout(const Timer::ms timeout);
    void                setupCylicRequest(const Timer::ms interval);

    // Cylic routines
    void                receiveRemoteRequest();
    void                sendCyclicRequest();
    void                pollButtons();
    void                updateLeds();

private:
    // Static helper functions
    static bool         stateToCStr(const state state, char* target);
    static state        stateFromCStr(const char* buffer);
    static state        parseJsonState(const char* buffer);

    BridgeServer*       getHttpServer();
    BridgeHttpClient*   getHttpClient();

    // 9Light interface methods
    void                sendStateRequest(const state state = state::UNDEFINED);


    // Configuration
    const api_config*   m_api_config;
    const led_config*   m_led_config;
    Map<state,pin>      m_button_map;
    Timer               m_button_timer;

    // Internal status
    state               m_state = state::UNDEFINED;
    Timer               m_cyclic_request_timer;

    // LED status
    Adafruit_NeoPixel*  m_pixels;
    state               m_leds_state = state::UNDEFINED;
    Animation*          m_animation;

    // 9Light server and client
    BridgeHttpClient*   m_http_client;
    BridgeServer*       m_http_server;
};

#endif /* _9LIGHT_H_ */