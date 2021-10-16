#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
#include <BridgeHttpClient.h>
#include <FastLED.h>

#define PIN_CALL      10
#define PIN_VIDEO     11
#define PIN_COFFEE    12
#define PIN_NONE      13

#define LED_PIN       9
#define LED_NUM       30
#define LED_TYPE      GRB

const char* const PROGMEM   API_ENDPOINT  = "http://srv-rpi3.m5a.bettgen.de";
const char* const PROGMEM   API_URL       = "/9light";
const unsigned int PROGMEM  API_PORT      = 9000;
const unsigned int PROGMEM  REMOTE_PORT   = 9001;

BridgeHttpClient http_client;
BridgeServer http_server(REMOTE_PORT);

CRGB leds[LED_NUM];
CRGB led_color(0, 0, 0);

void send_status_request(const char* status_value)
{
    char query[80] = {0};
    sprintf(query, "%s:%d%s/set?status=%s&remote", API_ENDPOINT, API_PORT, API_URL, status_value);
  
    SerialUSB.print(F("Sending HTTP request to: "));
    SerialUSB.println(query);
    http_client.get(query);

    char response[80] = {0};
    if (http_client.available()) {
        http_client.readBytesUntil('\n', response, sizeof(response)-1);
        SerialUSB.print(F("Got response: "));
        SerialUSB.println(response);

        parse_status(response);
    }
}

void parse_status(const char* buf)
{
    // Look for JSON key
    const char key[] = "\"status\":";
    char* pos = strstr(buf, key);
    if (pos == 0) return;

    // Skip any spaces
    pos += strlen(key);
    while (*pos++ == ' ');

    // Extract corresponding value (until end of buffer)
    char value[17] = {0};
    memcpy(value, pos, sizeof(value)-1);

    // Compare value
    const char status_none[]     = "none";
    const char status_call[]     = "call";
    const char status_video[]    = "video";
    const char status_request[]  = "request";
    const char status_coffee[]   = "coffee";

    if (memcmp(value, status_none, strlen(status_none)) == 0) {
        led_color = CRGB(0, 0, 0); 
    } else if (memcmp(value, status_call, strlen(status_call)) == 0) {
        led_color = CRGB(255, 150, 0); 
    } else if (memcmp(value, status_video, strlen(status_video)) == 0) {
        led_color = CRGB(255, 0, 0);
    } else if (memcmp(value, status_request, strlen(status_request)) == 0) {
        led_color = CRGB(0, 200, 250);
    } else if (memcmp(value, status_coffee, strlen(status_coffee)) == 0) {
        led_color = CRGB(0, 255, 0);
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

    http_server.noListenOnLocalhost();
    http_server.begin();
    
    pinMode(PIN_CALL,     INPUT_PULLUP);
    pinMode(PIN_VIDEO,    INPUT_PULLUP);
    pinMode(PIN_COFFEE,   INPUT_PULLUP);
    pinMode(PIN_NONE,     INPUT_PULLUP);

    FastLED.addLeds<WS2812, LED_PIN, LED_TYPE>(leds, LED_NUM);
}

void loop()
{
    BridgeClient client = http_server.accept();
    char request[80] = {0};
    size_t bytes;
    if (client) {
        // Find beginning of JSON payload (i.e. line starting with '{')
        do {
            memset(request, 0, sizeof(request));
            bytes = client.readBytesUntil('\n', request, sizeof(request));
            if (bytes == 0) return;
        } while(request[0] != '{');
        client.flush();
        client.print("HTTP/1.1 200 OK\n");
        
        SerialUSB.print("Incoming HTTP request: ");
        SerialUSB.println(request);
        parse_status(request);
    }
    client.stop();
  
    update_leds();
    
    if (digitalRead(PIN_CALL) == LOW) {
        send_status_request("call");
        delay(200);
    } else if (digitalRead(PIN_VIDEO) == LOW) {
        send_status_request("video");
        delay(200);
    } else if (digitalRead(PIN_COFFEE) == LOW) {
        send_status_request("coffee");        
        delay(200);
    } else if (digitalRead(PIN_NONE) == LOW) {
        send_status_request("none");
        delay(200);
    }
}
