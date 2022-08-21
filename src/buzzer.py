#!/usr/bin/env python3

"""Helper module for handling a buzzer acting as a classic door bell."""

from time import sleep
from typing import Optional
from threading import Thread
from RPi import GPIO

from constants import (
    BELL_BUZZER_SEQUENCE
)


class Buzzer:
    """Helper class handling the buzzer hardware."""
    def __init__(self, pin: int):
        self.pin: int = pin
        self._gpio_setup()
        self._ring_thread: Optional[Thread] = None

    def _gpio_setup(self) -> None:
        """Manages the internal GPIO setup."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)

    def ring(self) -> None:
        """Start an internal thread for the ring functionality of the bell."""
        if self._ring_thread and self._ring_thread.is_alive():
            return

        self._ring_thread = Thread(target=self._run_ring_thread, daemon=True)
        self._ring_thread.start()

    def _run_ring_thread(self) -> None:
        """Run the internal functions to trigger the buzzer once."""
        state: bool = True
        for timeout_ms in BELL_BUZZER_SEQUENCE:
            GPIO.output(self.pin, 1 if state else 0)
            state = not state
            sleep(timeout_ms / 1000)
        GPIO.output(self.pin, 0)
