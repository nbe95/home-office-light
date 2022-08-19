#!/usr/bin/env python3

""" Helper module for handling hardware button debouncing and managing the
corresponding callbacks."""

from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from typing import Optional, Callable


class StableButton():
    def __init__(self,
                 read_state_function: Callable[[], bool],
                 threshold: timedelta):
        self.threshold: timedelta = threshold
        self._read_state_function: Callable[[], bool] = read_state_function
        self._check_thread: Thread = Thread(
            target=self._run_check_thread,
            args=(self._read_state_function(),),
            daemon=True
        )
        self._check_abort: bool = False
        self._cb_pressed: Optional[Callable[[], None]] = None
        self._cb_released: Optional[Callable[[], None]] = None
        self._debounced_state: bool = False

    def set_callback_pressed(self, callback: Callable[[], None]) -> None:
        self._cb_pressed = callback

    def set_callback_released(self, callback: Callable[[], None]) -> None:
        self._cb_released = callback

    def get_debounced_state(self) -> bool:
        return self._debounced_state

    def trigger(self, _) -> None:
        if self._check_thread.is_alive():
            self._check_abort = True
            self._check_thread.join()

        self._check_abort = False
        self._check_thread.start()

    def _run_check_thread(self, state: bool) -> None:
        end: datetime = datetime.now() + self.threshold
        while datetime.now() < end:
            if self._check_abort or self._read_state_function() != state:
                return
            sleep(0.001)

        self._debounced_state = state
        if state and self._cb_pressed:
            self._cb_pressed()
        if not state and self._cb_released:
            self._cb_released()
