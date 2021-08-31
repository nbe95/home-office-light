#!/usr/bin/env python3

import enum
from threading import Thread
from transitions import Machine
from rpi_ws281x import *
import RPi.GPIO as GPIO
from time import sleep, time
from math import cos, pi
import flask
from random import randint

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

class Timeout(Thread):
    def __init__(self, func, timeout_s):
        super(Timeout, self).__init__()
        self.func = func
        self.timeout = timeout_s
        self.canceled = False
        self.start()

    def run(self):
        sleep(self.timeout)
        if not self.canceled:
            self.func()

class NineLight:
    timeout_request_s = 30

    def __init__(self, led_pin, button_pin, buzzer_pin):
        self.timer = None
        self.bell = self.Bell(self, button_pin, buzzer_pin)
        self.led = self.Led(self, led_pin)
        self.led.light_thread = None
        self.led.light_thread_terminate = False

    def getStatus(self):
        return self.state.name.lower()

    def setStatus(self, target):
        try:
            self.trigger(target)
        except:
            return False
        return True

    def onStateChange(self):
        self.led.setupLightThread()

    def on_enter_REQUEST(self):
        self.bell.ring()
        self.timer = Timeout(self.video, self.timeout_request_s)

    def on_exit_REQUEST(self):
        self.timer.canceled = True

    class Bell:
        def __init__(self, parent, button, buzzer):
            self.parent = parent
            self.button = button
            self.buzzer = buzzer
            self.setup()

        def setup(self):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.button, GPIO.IN)
            GPIO.setup(self.buzzer, GPIO.OUT)
            GPIO.add_event_detect(self.button, GPIO.RISING, callback=self.press, bouncetime=1000)

        def press(self, channel):
            self.parent.request()

        def ring(self):
            self.ring_thread = Thread(target=self.ringThread, daemon=True)
            self.ring_thread.start()

        def ringThread(self):
            for i in range(5):
                GPIO.output(self.buzzer, 1)
                sleep(0.05)
                GPIO.output(self.buzzer, 0)
                sleep(0.05)

        def cleanup(self):
            GPIO.cleanup()

    class Led:
        led_configuration = [
            13,     # number of LED pixels
            18,     # GPIO pin connected to the pixels (18 uses PWM!)
            800000, # LED signal frequency in hertz (usually 800khz)
            10,     # DMA channel to use for generating signal (try 10)
            False,  # True to invert the signal (when using NPN transistor level shift)
            255,    # set to 0 for darkest and 255 for brightest
            0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        ]

        def __init__(self, parent, led_pin):
            self.parent = parent
            self.led_configuration[1] = led_pin
            self.strip = Adafruit_NeoPixel(*self.led_configuration)
            self.strip.begin()
            self.clearAllPixels()

        def setAllPixels(self, color_rgb, top=False, bottom=False):
            if top:
                for p in range(0, 6):
                    self.strip.setPixelColorRGB(p, *color_rgb)
            if bottom:
                for p in range(7, 13):
                    self.strip.setPixelColorRGB(p, *color_rgb)
            self.strip.show()

        def setBrightness(self, brightness):
            self.strip.setBrightness(brightness)
            self.strip.show()

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
            if self.parent.state == States.CALL:
                self.setAllPixels((255, 150, 0), bottom=True)

            elif self.parent.state == States.VIDEO:
                self.setAllPixels((255, 0, 0), top=True)

            elif self.parent.state == States.REQUEST:
                self.setAllPixels((0, 200, 250), top=True)
                self.light_wave = PulseWave(0.8, 30, 255)
                while (self.light_thread_terminate != True):
                    self.setBrightness(self.light_wave.getInt())
                    sleep(0.02)

            elif self.parent.state == States.UNICORN:
                pos = True
                while (self.light_thread_terminate != True):
                    col = self.getRandomColor()
                    self.clearAllPixels()
                    self.setAllPixels(col, top=pos, bottom=not(pos))
                    sleep(0.05)
                    pos = not(pos)

        def getRandomColor(self):
            col = []
            for i in range(3):
                col.append(int(randint(0, 10) * 255 / 10))
            return col

nl = NineLight(18, 23, 24)
api = flask.Flask(__name__)

@api.route('/9light/set', methods=['GET'])
def api_set():
    target = flask.request.args.get("status")
    nl.setStatus(target)
    return flask.jsonify({"status": nl.getStatus()})

@api.route('/9light/get', methods=['GET'])
def api_get():
    return flask.jsonify({"status": nl.getStatus()})


def main():
    transitions = [
        { 'trigger': 'none', 'source': '*', 'dest': States.NONE },
        { 'trigger': 'call', 'source': '*', 'dest': States.CALL },
        { 'trigger': 'video', 'source': '*', 'dest': States.VIDEO },
        { 'trigger': 'request', 'source': States.VIDEO, 'dest': States.REQUEST },
        { 'trigger': 'unicorn', 'source': States.NONE, 'dest': States.UNICORN }
    ]
    ma = Machine(nl, states=States, transitions=transitions, initial=States.NONE, after_state_change=nl.onStateChange)

    #api_thread = Thread(target=lambda a: api.run(host='0.0.0.0', port=5000), daemon=True)
    api.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    try:
        main()
    except:
        raise
        nl.bell.cleanup()
