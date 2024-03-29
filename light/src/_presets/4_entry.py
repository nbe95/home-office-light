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

on = True
try:
    while (True):
        for p in range(0, 6):
            strip.setPixelColor(p, Color(0, 255, 0) if on else Color(0, 0, 0))
        for p in range(7, 13):
            strip.setPixelColor(p, Color(0, 0, 0) if on else Color(0, 255, 0))
        strip.show()
        on = not on

        sleep(0.2)

except:
    raise
