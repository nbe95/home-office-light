#include <Bridge.h>
#include <BridgeHttpClient.h>

#define PIN_CALL    10
#define PIN_VIDEO   11
#define PIN_UNICORN 12
#define PIN_NONE    13


BridgeHttpClient http_client;
const char* const api PROGMEM = "http://srv-rpi3.m5a.bettgen.de:9000/9light";

void set_status(const char* status_value)
{
    char query[80] = {0};
    sprintf(query, "%s/set?status=%s", api, status_value);
  
    SerialUSB.print(F("Sending GET request to: "));
    SerialUSB.println(query);
    http_client.get(query);

    char response[80] = {0};
    if (http_client.available()) {
        http_client.readBytesUntil('\n', response, sizeof(response));
        SerialUSB.print(F("Got response: "));
        SerialUSB.print(response);
    }
}

void setup()
{
    Bridge.begin();
    SerialUSB.begin(115200);
    pinMode(PIN_CALL,     INPUT_PULLUP);
    pinMode(PIN_VIDEO,    INPUT_PULLUP);
    pinMode(PIN_UNICORN,  INPUT_PULLUP);
    pinMode(PIN_NONE,     INPUT_PULLUP);
}

void loop()
{
    if (digitalRead(PIN_CALL) == LOW) {
        set_status("call");
        delay(200);
    } else if (digitalRead(PIN_VIDEO) == LOW) {
        set_status("video");
        delay(200);
    } else if (digitalRead(PIN_UNICORN) == LOW) {
        set_status("unicorn");
        delay(200);
    } else if (digitalRead(PIN_NONE) == LOW) {
        set_status("none");
        delay(200);
    }
}
