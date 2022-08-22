#!/usr/bin/env python3

"""Helper module for handling of a WS281x LED strip."""

from datetime import timedelta
from time import sleep
from random import randint
from typing import List, Tuple
from rpi_ws281x import Adafruit_NeoPixel

from aux.bg_task import BgTask
from aux.pulse_wave import PulseWave
from states import States


# pylint: disable=C0103
rgb = Tuple[int, int, int]


class LedStrip:
    """Helper class for managing the two LED fields of our 9light using a WS281x
    LED strip."""
    def __init__(self,
                 led_pin: int,
                 leds_total: int,
                 leds_top: List[int],
                 leds_bottom: List[int]):
        self._leds_top: List[int] = leds_top
        self._leds_bottom: List[int] = leds_bottom
        self._strip = Adafruit_NeoPixel(
            # pylint: disable=C0301
            leds_total,     # Number of LED pixels
            led_pin,        # GPIO pin connected to the pixels (18 uses PWM!)
            800000,         # LED signal frequency in hertz (usually 800khz)
            10,             # DMA channel to use for generating signal (try 10)
            False,          # True to invert the signal (when using NPN transistor level shift)             # noqa: E501
            255,            # Set to 0 for darkest and 255 for brightest
            1 if led_pin in (13, 19, 41, 45, 53) else 0     # Set to '1' for GPIOs 13, 19, 41, 45 or 53     # noqa: E501
        )
        self._strip.begin()
        self.state: States = States.NONE
        self._light_task: BgTask = BgTask(self._run_light_task, (States.NONE,))
        self.clear()

    def cleanup(self) -> None:
        """Reset any GPIOs used in this module."""
        self._light_task.cancel()
        self.clear()

    def set_top(self, color: rgb) -> None:
        """Set the LED color of the top glass field."""
        for pixel in self._leds_top:
            self._strip.setPixelColorRGB(pixel, *color)
        self._strip.show()

    def set_bottom(self, color: rgb) -> None:
        """Set the LED color of the bottom glass field."""
        for pixel in self._leds_bottom:
            self._strip.setPixelColorRGB(pixel, *color)
        self._strip.show()

    def set_all(self, color: rgb) -> None:
        """Set the LED color of both glass fields."""
        self.set_top(color)
        self.set_bottom(color)

    def set_brightness(self, brightness: int) -> None:
        """Set the brightness of all LEDs on the strip."""
        self._strip.setBrightness(brightness)
        self._strip.show()

    def clear(self) -> None:
        """Turn off any LEDs."""
        self.set_all((0, 0, 0))
        self.set_brightness(255)

    def on_state_changed(self, state: States) -> None:
        """Callback to be triggered on any 9light state change."""
        self._light_task.restart((state,))

    def _run_light_task(self, state: States) -> None:
        """Internal method which controls the 9light LED lightning according to
        the provided status information."""
        self.clear()

        if state == States.CALL:
            yellow: rgb = (255, 150, 0)
            self.set_bottom(yellow)

        elif state == States.VIDEO:
            red: rgb = (255, 0, 0)
            self.set_top(red)

        elif state == States.REQUEST:
            blue: rgb = (0, 200, 255)
            self.set_top(blue)
            wave: PulseWave = PulseWave(timedelta(milliseconds=800), (30, 255))
            while not self._light_task.is_canceled():
                self.set_brightness(wave.get_scaled())
                sleep(0.02)

        elif state == States.COFFEE:
            top: bool = False
            while not self._light_task.is_canceled():
                color: rgb = LedStrip.get_random_color()
                self.clear()
                if top:
                    self.set_top(color)
                else:
                    self.set_bottom(color)
                sleep(0.05)
                top = not top

    @staticmethod
    def get_random_color() -> rgb:
        """Provides a random RGB color."""
        r: int = randint(0, 10) * 255 // 10
        g: int = randint(0, 10) * 255 // 10
        b: int = randint(0, 10) * 255 // 10
        return (r, g, b)
