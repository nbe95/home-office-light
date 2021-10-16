#!/usr/bin/env python3

import enum
from threading import Thread
from transitions import Machine
from rpi_ws281x import *
import RPi.GPIO as GPIO
from time import sleep, time
from math import cos, pi
import flask
from waitress import serve
from random import randint
import atexit


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

class StableButton():
    def __init__(self, cb_read_state, threshold_ms):
        self.threshold_ms = threshold_ms
        self.cb_read_state = cb_read_state
        self.cb_pressed = None
        self.cb_released = None
        self.check_thread = None
        self.check_abort = False

    def setCallbackPressed(self, cb):
        self.cb_pressed = cb

    def setCallbackReleased(self, cb):
        self.cb_released = cb

    def trigger(self, channel):
        if self.check_thread is not None and self.check_thread.is_alive():
            self.check_abort = True
            self.check_thread.join()

        state = self.cb_read_state()
        self.check_abort = False
        self.check_thread = Thread(target=self.checkThread, args=(state,), daemon=True)
        self.check_thread.start()

    def checkThread(self, state):
        end = time() + (self.threshold_ms / 1000)
        while time() < end:
            if self.check_abort or self.cb_read_state() != state:
                return False
            sleep(0.001)

        if state:
            if self.cb_pressed is not None:
                self.cb_pressed()
        else:
            if self.cb_released is not None:
                self.cb_released()
        return True

class NineLight:
    timeout_request_s = 30
    expiration_remotes_s = 60 * 60 * 6

    def __init__(self, led_pin, button_pin, buzzer_pin):
        self.timer = None
        self.remotes = []
        self.bell = self.Bell(self, button_pin, buzzer_pin)
        self.led = self.Led(self, led_pin)

    def getStatus(self):
        self.updateRemotes()
        status = {
            "status": self.state.name.lower(),
            "remotes:": list(r[0] for r in self.remotes)
        }
        return status

    def setStatus(self, target):
        try:
            self.trigger(target)
        except:
            return False
        return True

    def addRemote(self, ip, expiration_s = None):
        if expiration_s != None:
            expires = expiration_s
        else:
            expires = time() + self.expiration_remptes_s

        self.remotes.append((ip, expires))

    def updateRemotes(self):
        changed = False
        new_remotes = []
        for r in self.remotes:
            if r[1] <= time():
                changed = True
            else:
                new_remotes.append(r)

        if changed:
            self.remotes = new_remotes

    def onStateChange(self):
        self.updateRemotes()
        self.led.setupLightThread()

    def on_enter_VIDEO(self):
        self.timer = Timeout(self.bell.enable, 2)

    def on_exit_VIDEO(self):
        self.bell.disable()
        self.timer.canceled = True

    def on_enter_REQUEST(self):
        self.bell.ring()
        self.timer = Timeout(self.video, self.timeout_request_s)

    def on_exit_REQUEST(self):
        self.timer.canceled = True

    def cleanup(self):
        self.bell.cleanup()

    class States(enum.Enum):
        NONE = 0
        CALL = 1
        VIDEO = 2
        REQUEST = 3
        COFFEE = 99

    class Bell:
        def __init__(self, parent, button, buzzer):
            self.enabled = False
            self.parent = parent
            self.button = button
            self.buzzer = buzzer
            self.stable_button = StableButton(self.readButton, 50)
            self.setup()

        def setup(self):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.button, GPIO.IN)
            GPIO.setup(self.buzzer, GPIO.OUT)
            self.stable_button.setCallbackPressed(self.press)
            GPIO.add_event_detect(self.button, GPIO.BOTH, callback=self.stable_button.trigger)

        def readButton(self):
            return GPIO.input(self.button)

        def disable(self):
            self.enabled = False

        def enable(self):
            self.enabled = True

        def press(self):
            if self.enabled:
                self.parent.request()

        def ring(self):
            self.ring_thread = Thread(target=self.ringThread, daemon=True)
            self.ring_thread.start()

        def ringThread(self):
            for i in range(5):
                GPIO.output(self.buzzer, 1)
                sleep(0.1)
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

            self.light_thread = None
            self.light_thread_terminate = False

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
            if self.parent.state == self.parent.States.CALL:
                yellow = (255, 150, 0)
                self.setAllPixels(yellow, bottom=True)

            elif self.parent.state == self.parent.States.VIDEO:
                red = (255, 0, 0)
                self.setAllPixels(red, top=True)

            elif self.parent.state == self.parent.States.REQUEST:
                blue = (0, 200, 255)
                self.setAllPixels(blue, top=True)
                self.light_wave = PulseWave(0.8, 30, 255)
                while (self.light_thread_terminate != True):
                    self.setBrightness(self.light_wave.getInt())
                    sleep(0.02)

            elif self.parent.state == self.parent.States.COFFEE:
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

@api.route('/')
def api_redirect():
    return flask.redirect('/9light/')

@api.route('/9light/')
def api_help():
    return flask.send_file('api.htm')

@api.route('/9light/set', methods=['GET'])
def api_set():
    target = flask.request.args.get("status")
    nl.setStatus(target)

    is_remote = ("remote" in flask.request.args)
    if is_remote:
        nl.addRemote(flask.request.remote_addr)

    return flask.jsonify(nl.getStatus())

@api.route('/9light/get', methods=['GET'])
def api_get():
    return flask.jsonify(nl.getStatus())


def main():
    transitions = [
        { 'trigger': 'none', 'source': '*', 'dest': nl.States.NONE },
        { 'trigger': 'call', 'source': '*', 'dest': nl.States.CALL },
        { 'trigger': 'video', 'source': '*', 'dest': nl.States.VIDEO },
        { 'trigger': 'request', 'source': nl.States.VIDEO, 'dest': nl.States.REQUEST },
        { 'trigger': 'coffee', 'source': nl.States.NONE, 'dest': nl.States.COFFEE }
    ]
    ma = Machine(nl, states=nl.States, transitions=transitions, initial=nl.States.NONE, after_state_change=nl.onStateChange)

    serve(api, host='0.0.0.0', port=9000)
    atexit.register(nl.cleanup)

if __name__ == "__main__":
    main()
