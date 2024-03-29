#!/usr/bin/env python3

"""Helper module for handling the HomeOfficeLight bell button."""

from datetime import datetime, timedelta
from time import sleep
from typing import Callable, Optional

from RPi import GPIO

from aux.bg_task import BgTask
from constants import BELL_DEBOUNCE_TIME


class Button:
    """Helper class for handling and debouncing the button."""

    def __init__(
        self,
        pin: int,
        callback_pressed: Optional[Callable[[], None]] = None,
        callback_released: Optional[Callable[[], None]] = None,
        threshold: timedelta = BELL_DEBOUNCE_TIME,
    ):
        self.pin: int = pin
        self.threshold: timedelta = threshold
        self._cb_pressed: Optional[Callable[[], None]] = callback_pressed
        self._cb_released: Optional[Callable[[], None]] = callback_released
        self._gpio_setup()
        self._debounce_task: BgTask = BgTask(self._run_debounce_task, (False,))
        self.debounced: bool = False

    def _gpio_setup(self) -> None:
        """Manages the internal GPIO setup."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.on_gpio_edge)

    def cleanup(self) -> None:
        """Reset any GPIOs used in this module."""
        self._debounce_task.cancel()
        GPIO.cleanup()

    def get_button_state(self) -> bool:
        """Fetches the current button state as a boolean value."""
        return GPIO.input(self.pin)  # type: ignore

    def on_gpio_edge(self, _) -> None:
        """Internal method which must be called upon ANY detected edge of the
        button (i.e. by the bare GPIO functionalities)."""
        self._debounce_task.restart((self.get_button_state(),))

    def _run_debounce_task(self, state: bool) -> None:
        """Perform internally debouncing operations."""
        end: datetime = datetime.now() + self.threshold
        while datetime.now() < end:
            if (
                self._debounce_task.is_canceled()
                or self.get_button_state() != state
            ):
                return
            sleep(0.001)

        self.debounced = state
        if state and self._cb_pressed:
            self._cb_pressed()
        if not state and self._cb_released:
            self._cb_released()
