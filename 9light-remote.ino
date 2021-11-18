#include <Adafruit_NeoPixel.h>
//#include <avr/power.h>
#include "src/9light.h"


const NineLightRemote::led_config led_config = {
    .do_pin         = 9,
    .num_leds       = 30,
    .options        = NEO_GRB + NEO_KHZ800
};

const NineLightRemote::api_config api_config = {
    .endpoint       = "http://srv-rpi3.m5a.bettgen.de",
    .url            = "/9light",
    .port           = 9000,
    .remote_port    = 9001
};

NineLightRemote Remote(&api_config, &led_config);


void setup()
{
    // Setup bridge and serial interface
    Bridge.begin();
    SerialUSB.begin(115200);

    // Register remote buttons
    Remote.registerButton(NineLightRemote::state::CALL,     10,     40);
    Remote.registerButton(NineLightRemote::state::VIDEO,    11,     40);
    Remote.registerButton(NineLightRemote::state::COFFEE,   12,     40);
    Remote.registerButton(NineLightRemote::state::NONE,     13,     40);

    // Setup automatic status requests after being idle (keep remote registration status)
    Remote.setupIdleRequest(2UL * 60 * 60 * 1000);

    // Query initial state
    Remote.sendStateRequest();
}


void loop()
{
    // Call cyclic processes
    Remote.receiveRemoteRequest();
    Remote.sendRequestIfIdle();
    Remote.pollButtons();
    Remote.updateLeds();
}
