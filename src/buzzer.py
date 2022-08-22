#!/usr/bin/env python3

"""Helper module for handling a buzzer acting as a classic door bell."""

from time import sleep
from RPi import GPIO

from bg_task import BgTask
from constants import (
    BELL_BUZZER_SEQUENCE
)


class Buzzer:
    """Helper class handling the buzzer hardware."""
    def __init__(self, pin: int):
        self.pin: int = pin
        self._gpio_setup()
        self._ring_task: BgTask = BgTask(self._run_ring_task)

    def _gpio_setup(self) -> None:
        """Manages the internal GPIO setup."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)

    def cleanup(self) -> None:
        """Reset any GPIOs used in this module."""
        GPIO.cleanup()

    def ring(self) -> None:
        """Start an internal thread for the ring functionality of the bell."""
        if not self._ring_task.is_running():
            self._ring_task.restart()

    def _run_ring_task(self) -> None:
        """Run the internal functions to trigger the buzzer once."""
        state: bool = True
        for timeout_ms in BELL_BUZZER_SEQUENCE:
            if self._ring_task.is_canceled():
                break
            GPIO.output(self.pin, 1 if state else 0)
            state = not state
            sleep(timeout_ms / 1000)
        GPIO.output(self.pin, 0)
