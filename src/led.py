#!/usr/bin/env python3

"""Helper module for handling of a WS281x LED strip."""

from rpi_ws281x import Adafruit_NeoPixel
from time import sleep
from threading import Thread
from random import randint
from typing import List, Tuple, Optional

from pulse_wave import PulseWave
from nine_light import NineLight


# Type alias
rgb = Tuple[int, int, int]


class LedStrip:
    def __init__(self,
                 led_pin: int,
                 leds_total: int,
                 leds_top: Tuple[int, int],
                 leds_bottom: Tuple[int, int]):
        self._leds_top: range = range(leds_top[0], leds_top[1] + 1)
        self._leds_bottom: range = range(leds_bottom[0], leds_bottom[1] + 1)
        self._strip = Adafruit_NeoPixel(*(
            leds_total,     # Number of LED pixels
            led_pin,        # GPIO pin connected to the pixels (18 uses PWM!)
            800000,         # LED signal frequency in hertz (usually 800khz)
            10,             # DMA channel to use for generating signal (try 10)
            False,          # True to invert the signal (when using NPN transistor level shift)             # noqa: E501
            255,            # Set to 0 for darkest and 255 for brightest
            1 if led_pin in (13, 19, 41, 45, 53) else 0     # Set to '1' for GPIOs 13, 19, 41, 45 or 53     # noqa: E501
        ))
        self._strip.begin()

        self.clear_all_pixels()

        self._light_thread: Optional[Thread] = None
        self._light_thread_terminate: bool = False

    def set_top(self, color: rgb) -> None:
        for pixel in self._leds_top:
            self.strip.setPixelColorRGB(pixel, *color)
        self.strip.show()

    def set_bottom(self, color: rgb) -> None:
        for pixel in self._leds_bottom:
            self.strip.setPixelColorRGB(pixel, *color)
        self.strip.show()

    def set_all(self, color: rgb) -> None:
        self.set_top(color)
        self.set_bottom(color)

    def set_brightness(self, brightness: int) -> None:
        self.strip.setBrightness(brightness)
        self.strip.show()

    def clear(self) -> None:
        self.set_all((0, 0, 0))
        self.set_brightness(255)

    def on_state_changed(self, state: NineLight.States) -> None:
        if self._light_thread:
            self._light_thread_terminate = True
            self._light_thread.join()

        self._light_thread_terminate = False
        self._light_thread = Thread(
            target=self._run_light_thread,
            args=(state,),
            daemon=True
        )
        self._light_thread.start()

    def _run_light_thread(self, state: NineLight.States) -> None:
        self.clear()

        if state == NineLight.States.CALL:
            yellow: rgb = (255, 150, 0)
            self.set_bottom(yellow)

        elif state == NineLight.States.VIDEO:
            red: rgb = (255, 0, 0)
            self.set_top(red)

        elif state == NineLight.States.REQUEST:
            blue: rgb = (0, 200, 255)
            self.set_top(blue)
            self.light_wave = PulseWave(0.8, 30, 255)
            while (not self.light_thread_terminate):
                self.setBrightness(self.light_wave.getInt())
                sleep(0.02)

        elif state == NineLight.States.COFFEE:
            top: bool = False
            while (not self.light_thread_terminate):
                color: rgb = LedStrip.get_random_color()
                self.clear()
                if top:
                    self.set_top(color)
                else:
                    self.set_bottom(color)
                sleep(0.05)
                top = not(top)

    @staticmethod
    def get_random_color() -> rgb:
        color: List[int] = []
        for _ in range(3):
            color.append(int(randint(0, 10) * 255 / 10))
        return tuple(color)
