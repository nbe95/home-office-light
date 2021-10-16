#!/usr/bin/env python3

from rpi_ws281x import *
from time import sleep
from math import cos, pi

# LED strip configuration
LED_COUNT      = 13      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()


for p in range(0, 7):
    strip.setPixelColorRGB(p, 0, 200, 255)

period = 800
frame_time = 5
frames = list(t/1000 for t in range(0, period, frame_time)) # 2sec period, 5ms framerate
brightness = list(int((cos(t * 2 * pi)/2+0.5) * (255 - 30) + 30) for t in frames)

while (True):
    for b in brightness:
        strip.setBrightness(b)
        strip.show()
        sleep(frame_time / 1000)
