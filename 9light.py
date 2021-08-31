#!/usr/bin/env python3

import enum
from threading import Thread
from transitions import Machine
from rpi_ws281x import *
from time import sleep, time
from math import cos, pi

class States(enum.Enum):
    NONE = 0
    CALL = 1
    VIDEO = 2
    REQUEST = 3
    UNICORN = 99

class PulseWave:
    def __init__(self, period_s, min_val, max_val):
        self.period_s = period_s
        self.min_val = min_val
        self.max_val = max_val
        self.reset()

    def reset(self):
        self.start_time = time()

    def getInt(self):
        t = time() - self.start_time
        cosine = 0.5 * (cos(2 * pi * t / self.period_s) + 1)
        return int(cosine * (self.max_val - self.min_val) + self.min_val)

class NineLight:
    def __init__(self):
        self.light_thread = None
        self.light_thread_terminate = False

        # LED strip configuration
        led_count      = 13      # Number of LED pixels.
        led_pin        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        led_freq_hz    = 800000  # LED signal frequency in hertz (usually 800khz)
        led_dma        = 10      # DMA channel to use for generating signal (try 10)
        led_brightness = 255     # Set to 0 for darkest and 255 for brightest
        led_invert     = False   # True to invert the signal (when using NPN transistor level shift)
        led_channel    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.led_strip = Adafruit_NeoPixel(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
        self.led_strip.begin()

    def setAllPixels(self, color_rgb, top=False, bottom=False):
        if top:
            for p in range(0, 7):
                self.led_strip.setPixelColorRGB(p, *color_rgb)
        if bottom:
            for p in range(7, 13):
                self.led_strip.setPixelColorRGB(p, *color_rgb)
        self.led_strip.show()

    def setBrightness(self, brightness):
        self.led_strip.setBrightness(brightness)
        self.led_strip.show()

    def clearAllPixels(self):
        self.setAllPixels((0, 0, 0), top=True, bottom=True)
        self.setBrightness(255)

    def setupLightThread(self):
        if self.light_thread is not None:
            self.light_thread_terminate = True
            self.light_thread.join()

        self.light_thread_terminate = False
        self.light_thread = Thread(target=self.lightThread, daemon=True)
        self.light_thread.start()

    def lightThread(self):
        self.clearAllPixels()
        if self.state == States.CALL:
            self.setAllPixels((255, 150, 0), top=False, bottom=True)

        elif self.state == States.VIDEO:
            self.setAllPixels((255, 0, 0), top=True, bottom=False)

        elif self.state == States.REQUEST:
            self.setAllPixels((0, 200, 250), top=True, bottom=False)
            self.light_wave = PulseWave(0.8, 30, 255)
            while (self.light_thread_terminate != True):
                self.setBrightness(self.light_wave.getInt())
                sleep(0.02)

def main():
    nl = NineLight()
    transitions = [
        { 'trigger' : 'none', 'source': '*', 'dest': States.NONE, 'after': nl.setupLightThread },
        { 'trigger' : 'call', 'source': '*', 'dest': States.CALL, 'after': nl.setupLightThread },
        { 'trigger' : 'video', 'source': '*', 'dest': States.VIDEO, 'after': nl.setupLightThread },
        { 'trigger' : 'request', 'source': States.VIDEO, 'dest': States.REQUEST, 'after': nl.setupLightThread },
        { 'trigger' : 'unicorn', 'source': '*', 'dest': States.UNICORN, 'after': nl.setupLightThread }
    ]
    ma = Machine(nl, states=States, transitions=transitions, initial=States.NONE)

    nl.call()
    sleep(3)
    nl.video()
    sleep(3)
    nl.request()
    sleep(3)
    nl.unicorn()
    sleep(3)
    nl.none()

if __name__ == "__main__":
        main()
