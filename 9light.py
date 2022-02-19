#!/usr/bin/env python3

import enum
from threading import Thread
from urllib import request
from transitions import Machine
from rpi_ws281x import *
import RPi.GPIO as GPIO
from time import sleep, time
from math import cos, pi
import flask
import subprocess
import shlex
import json
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
        self.threshold_ms   = threshold_ms
        self.cb_read_state  = cb_read_state
        self.cb_pressed     = None
        self.cb_released    = None
        self.check_thread   = None
        self.check_abort    = False
        self.debounced      = False

    def setCallbackPressed(self, cb):
        self.cb_pressed = cb

    def setCallbackReleased(self, cb):
        self.cb_released = cb

    def getDebouncedState(self):
        return self.debounced

    def trigger(self, _):
        if self.check_thread is not None and self.check_thread.is_alive():
            self.check_abort = True
            self.check_thread.join()

        state = self.cb_read_state()
        self.check_abort = False
        self.check_thread = Thread(target = self.checkThread, args = (state,), daemon = True)
        self.check_thread.start()

    def checkThread(self, state):
        end = time() + (self.threshold_ms / 1000)
        while time() < end:
            if self.check_abort or self.cb_read_state() != state:
                return False
            sleep(0.001)

        self.debounced = state
        if state:
            if self.cb_pressed is not None:
                self.cb_pressed()
        else:
            if self.cb_released is not None:
                self.cb_released()
        return True

class NineLight:
    def __init__(self, local_port, remotes_port, led_pin, button_pin, buzzer_pin):
        self.timer                  = None
        self.remotes                = []
        self.bell                   = self.Bell(self, button_pin, buzzer_pin)
        self.led                    = self.Led(self, led_pin)
        self.local_http_port        = local_port
        self.remotes_http_port      = remotes_port
        self.remotes_expiration_s   = 60 * 60 * 3
        self.remotes_skip_once      = None
        self.timeout_request_s      = 30

        self.state = self.States.NONE
        self.led.setupLightThread()

    def getStatus(self):
        self.updateRemotes()
        status = {
            "status": self.state.name.lower(),
            "remotes": list(r[0] for r in self.remotes)
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
            expires = time() + self.remotes_expiration_s

        for r in self.remotes:
            if r[0] == ip:
                self.remotes.remove(r)

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

    def sendToRemotes(self):
        self.updateRemotes()
        payload = json.dumps(self.getStatus())
        for r in self.remotes:
            if r[0] != self.remotes_skip_once:
                cmd = "curl -fs -X GET \"http://{}:{}/9light/remote\" -d '{}' > /dev/null".format(r[0], self.remotes_http_port, payload)
                subprocess.Popen(shlex.split(cmd))
        self.remotes_skip_once = None

    def onStateChange(self):
        self.led.setupLightThread()
        self.sendToRemotes()

    def on_exit_NONE(self):
        self.led.light_show.reset()

    def on_exit_VIDEO(self):
        if self.timer is not None:
            self.timer.canceled = True

    def on_enter_REQUEST(self):
        self.bell.ring()
        if self.timer is not None:
            self.timer = Timeout(self.video, self.timeout_request_s)

    def on_exit_REQUEST(self):
        if self.timer is not None:
            self.timer.canceled = True

    def cleanup(self):
        self.bell.cleanup()

    class States(enum.Enum):
        NONE    = 0
        CALL    = 1
        VIDEO   = 2
        REQUEST = 3
        COFFEE  = 99

    class Bell:
        def __init__(self, parent, button, buzzer):
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
            GPIO.add_event_detect(self.button, GPIO.BOTH, callback = self.stable_button.trigger)

        def readButton(self):
            return GPIO.input(self.button)

        def press(self):
            self.parent.request()

        def ring(self):
            self.ring_thread = Thread(target = self.ringThread, daemon = True)
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
            self.light_show = self.LightShow(self.strip, 0.05, 2)

        def setAllPixels(self, color_rgb, top = False, bottom = False):
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
            self.setAllPixels((0, 0, 0), top = True, bottom = True)
            self.setBrightness(255)

        def setupLightThread(self):
            if self.light_thread is not None:
                self.light_thread_terminate = True
                self.light_thread.join()

            self.light_thread_terminate = False
            self.light_thread = Thread(target = self.lightThread, daemon = True)
            self.light_thread.start()

        def lightThread(self):
            self.clearAllPixels()

            if self.parent.state == self.parent.States.NONE:
                is_ready = False
                while (not self.light_thread_terminate):
                    button_pressed = self.parent.bell.stable_button.getDebouncedState()
                    if is_ready:
                        self.light_show.process(button_pressed)
                    elif not button_pressed:
                        is_ready = True
                    sleep(0.01)

            elif self.parent.state == self.parent.States.CALL:
                yellow = (255, 150, 0)
                self.setAllPixels(yellow, bottom = True)

            elif self.parent.state == self.parent.States.VIDEO:
                red = (255, 0, 0)
                self.setAllPixels(red, top = True)

            elif self.parent.state == self.parent.States.REQUEST:
                blue = (0, 200, 255)
                self.setAllPixels(blue, top = True)
                self.light_wave = PulseWave(0.8, 30, 255)
                while (not self.light_thread_terminate):
                    self.setBrightness(self.light_wave.getInt())
                    sleep(0.02)

            elif self.parent.state == self.parent.States.COFFEE:
                pos = True
                while (not self.light_thread_terminate):
                    col = NineLight.Led.getRandomColor()
                    self.clearAllPixels()
                    self.setAllPixels(col, top = pos, bottom = not(pos))
                    sleep(0.05)
                    pos = not(pos)

        def getRandomColor():
            col = []
            for i in range(3):
                col.append(int(randint(0, 10) * 255 / 10))
            return tuple(col)

        def getRainbowColor(pos):
            # See lightshow.py
            # in = 0..255, out = magic
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
            return (0, pos * 3, 255 - pos * 3)

        class LightShow:
            def __init__(self, strip, period_s, spare_leds):
                self.total_leds = 12
                self.strip = strip
                self.period_s = period_s
                self.spare_leds = spare_leds
                self.reset()

            def reset(self):
                self.spare_count = 0
                self.last_call = 0
                self.leds = [(0, 0, 0)] * self.total_leds

            def isRunning(self):
                return any([any(col) for col in self.leds])

            def process(self, continue_pixels):
                # Check interval from last call
                if self.last_call + self.period_s > time():
                    return
                self.last_call = time()

                # Prepare new pixel
                new_pixel = (0, 0, 0)
                self.spare_count += 1
                if self.spare_count > self.spare_leds or not self.isRunning():
                    self.spare_count = 0
                    if continue_pixels:
                        new_pixel = NineLight.Led.getRainbowColor(int(time() / self.period_s * 1000) % 255)

                # Shift pixels forward
                running_before = self.isRunning()
                self.leds.pop()
                self.leds.insert(0, new_pixel)

                # Check if we have something to do
                if not running_before and not self.isRunning():
                    return

                # Apply pixels to LED strip
                pixel_id_per_led = (*range(0, 6), *range(7, 13))
                i = 0
                for col in self.leds: 
                    self.strip.setPixelColorRGB(pixel_id_per_led[i], *col)
                    i += 1
                self.strip.show()


nl = NineLight(9000, 9001, 18, 23, 24)
api = flask.Flask(__name__)

@api.route('/')
def api_redirect():
    return flask.redirect('/9light/')

@api.route('/9light/')
def api_help():
    return flask.send_file('api.htm')

@api.route('/9light/set', methods=['GET'])
def api_set():
    is_remote = ("remote" in flask.request.args)
    if is_remote:
        nl.addRemote(flask.request.remote_addr)
        nl.remotes_skip_once = flask.request.remote_addr

    target = flask.request.args.get("status")
    nl.setStatus(target)

    return flask.jsonify(nl.getStatus())

@api.route('/9light/get', methods=['GET'])
def api_get():
    is_remote = ("remote" in flask.request.args)
    if is_remote:
        nl.addRemote(flask.request.remote_addr)

    return flask.jsonify(nl.getStatus())


def main():
    transitions = [
        { 'trigger': 'none',    'source': '*',              'dest': nl.States.NONE },
        { 'trigger': 'call',    'source': '*',              'dest': nl.States.CALL },
        { 'trigger': 'video',   'source': '*',              'dest': nl.States.VIDEO },
        { 'trigger': 'request', 'source': nl.States.VIDEO,  'dest': nl.States.REQUEST },
        { 'trigger': 'request', 'source': nl.States.COFFEE, 'dest': nl.States.NONE },
        { 'trigger': 'coffee',  'source': nl.States.NONE,   'dest': nl.States.COFFEE }
    ]
    ma = Machine(nl, states = nl.States, transitions = transitions, initial = nl.States.NONE, after_state_change = nl.onStateChange)

    serve(api, host='0.0.0.0', port = nl.local_http_port)
    atexit.register(nl.cleanup)

if __name__ == "__main__":
    main()
