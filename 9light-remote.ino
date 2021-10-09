#include <Bridge.h>
#include <BridgeHttpClient.h>
#include <FastLED.h>

#define PIN_CALL    10
#define PIN_VIDEO   11
#define PIN_UNICORN 12
#define PIN_NONE    13

#define LED_PIN     9
#define LED_NUM     30
#define LED_TYPE    GRB

BridgeHttpClient http_client;
const char* const api PROGMEM = "http://srv-rpi3.m5a.bettgen.de:9000/9light";

CRGB leds[LED_NUM];
CRGB led_color(0, 0, 0);

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
        SerialUSB.println(response);

        const char response_call[]    = "{\"status\":\"call\"}";
        const char response_video[]   = "{\"status\":\"video\"}";
        const char response_unicorn[] = "{\"status\":\"unicorn\"}";
        const char response_request[] = "{\"status\":\"request\"}";
        const char response_none[]    = "{\"status\":\"none\"}";

        if (memcmp(response, response_none, sizeof(response_none)) == 0) {
            led_color = CRGB(0, 0, 0); 
        } else if (memcmp(response, response_call, sizeof(response_call)) == 0) {
            led_color = CRGB(255, 150, 0); 
        } else if (memcmp(response, response_video, sizeof(response_video)) == 0) {
            led_color = CRGB(255, 0, 0);
        } else if (memcmp(response, response_request, sizeof(response_request)) == 0) {
            led_color = CRGB(0, 200, 255);
        } else if (memcmp(response, response_unicorn, sizeof(response_unicorn)) == 0) {
            led_color = CRGB(0, 255, 0);
        }   
    }
}

void update_leds(const bool wave = true)
{
    CRGB rgb = led_color;
    if (wave) {
        const float period_s = 2.0;
        const int min_val = 40;
        const int max_val = 255;
        
        float cosine = 0.5 * (cos(TWO_PI * millis() / 1000 / period_s) + 1);
        float brightness = cosine * (max_val - min_val) + min_val;

        rgb[0] = int(rgb[0] * brightness / 255);
        rgb[1] = int(rgb[1] * brightness / 255);
        rgb[2] = int(rgb[2] * brightness / 255);
    }

    for (int i = 0; i < LED_NUM; i++) {
        leds[i] = rgb;
    }
    FastLED.show();
}

void setup()
{
    Bridge.begin();
    SerialUSB.begin(115200);
    
    pinMode(PIN_CALL,     INPUT_PULLUP);
    pinMode(PIN_VIDEO,    INPUT_PULLUP);
    pinMode(PIN_UNICORN,  INPUT_PULLUP);
    pinMode(PIN_NONE,     INPUT_PULLUP);

    FastLED.addLeds<WS2812, LED_PIN, LED_TYPE>(leds, LED_NUM);
}

void loop()
{
    update_leds();
    
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
