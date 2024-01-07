// Copyright (c) 2022 Niklas Bettgen

#include <Adafruit_NeoPixel.h>
#include "src/light-remote.h"


const LightRemote::led_config led_config = {
    .do_pin         = Pin(9, OUTPUT),
    .num_leds       = 30,
    .options        = NEO_GRB + NEO_KHZ800
};

const LightRemote::api_config api_config = {
    .endpoint       = "http://192.168.1.21",
    .uri_get        = "/state/get",
    .uri_set        = "/state/set",
    .port           = 9000,
    .remote_port    = 9001
};

LightRemote Remote(&api_config, &led_config);


void setup() {
    // Setup bridge and serial interface
    Bridge.begin();
    SerialUSB.begin(115200);

    // Register remote buttons
    Remote.registerButton(LightRemote::state::CALL,     Pin(10, INPUT_PULLUP),  40);
    Remote.registerButton(LightRemote::state::VIDEO,    Pin(11, INPUT_PULLUP),  40);
    Remote.registerButton(LightRemote::state::COFFEE,   Pin(12, INPUT_PULLUP),  40);
    Remote.registerButton(LightRemote::state::NONE,     Pin(13, INPUT_PULLUP),  40);

    // Setup automatic state requests after being idle (keep remote registration state)
    Remote.setupIdleRequest(2UL * 60 * 60 * 1000);

    // Query initial state
    Remote.sendStateRequest();
}


void loop() {
    // Call cyclic processes
    Remote.receiveRemoteRequest();
    Remote.sendRequestIfIdle();
    Remote.pollButtons();
    Remote.updateLeds();
}
