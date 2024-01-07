// Copyright (c) 2022 Niklas Bettgen

#include <Adafruit_NeoPixel.h>
#include "src/9light-remote.h"


const NineLightRemote::led_config led_config = {
    .do_pin         = Pin(9, OUTPUT),
    .num_leds       = 30,
    .options        = NEO_GRB + NEO_KHZ800
};

const NineLightRemote::api_config api_config = {
    .endpoint       = "http://192.168.1.21",
    .uri_get        = "/state/get",
    .uri_set        = "/state/set",
    .port           = 9000,
    .remote_port    = 9001
};

NineLightRemote Remote(&api_config, &led_config);


void setup() {
    // Setup bridge and serial interface
    Bridge.begin();
    SerialUSB.begin(115200);

    // Register remote buttons
    Remote.registerButton(NineLightRemote::state::CALL,     Pin(10, INPUT_PULLUP),  40);
    Remote.registerButton(NineLightRemote::state::VIDEO,    Pin(11, INPUT_PULLUP),  40);
    Remote.registerButton(NineLightRemote::state::COFFEE,   Pin(12, INPUT_PULLUP),  40);
    Remote.registerButton(NineLightRemote::state::NONE,     Pin(13, INPUT_PULLUP),  40);

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
