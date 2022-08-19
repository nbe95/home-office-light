#!/usr/bin/env python3

"""Helper module for handling a button and a hardware buzzer acting as a classic
door bell."""

from time import sleep
from typing import Optional, Callable
from threading import Thread
from RPi import GPIO

from stable_button import StableButton
from constants import (
    BELL_DEBOUNCE_TIME,
    BELL_BUZZER_MS
)


class Bell:
    """Helper class handling the hardware of a button and a buzzer."""
    def __init__(self, button_pin: int, buzzer_pin: int):
        self.button_pin: int = button_pin
        self.buzzer_pin: int = buzzer_pin
        self._stable_button = StableButton(self.get_button_state,
                                           BELL_DEBOUNCE_TIME)
        self._gpio_setup()
        self._cb_request: Optional[Callable[[], None]]
        self._ring_thread: Thread = Thread(target=self._run_ring_thread,
                                           daemon=True)

    def set_callback_request(self, callback: Callable[[], None]) -> None:
        """Set the callback function to be triggered when the button is
        pushed."""
        self._cb_request = callback

    def _gpio_setup(self) -> None:
        """Manages the internal GPIO setup."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        self._stable_button.set_callback_pressed(self.on_button_pressed)
        GPIO.add_event_detect(
            self.button_pin,
            GPIO.BOTH,
            callback=self._stable_button.trigger
        )

    def get_button_state(self) -> bool:
        """Fetches the current button state as a boolean value."""
        return GPIO.input(self.button_pin)

    def on_button_pressed(self) -> None:
        """Callback to be triggered when the button is pressed."""
        if self._cb_request:
            self._cb_request()

    def ring(self) -> None:
        """Start an internal thread for the ring functionality of the bell."""
        self._ring_thread.start()

    def _run_ring_thread(self) -> None:
        """Run the internal functions to trigger the buzzer once."""
        state: bool = True
        for timeout_ms in BELL_BUZZER_MS:
            GPIO.output(self.buzzer_pin, 1 if state else 0)
            state = not state
            sleep(timeout_ms // 1000)

    @staticmethod
    def cleanup() -> None:
        """Perform some clean-up of the GPIO module."""
        GPIO.cleanup()
