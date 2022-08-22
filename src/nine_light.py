#!/usr/bin/env python3

"""Python module which handles the main 9light interfaces and functions."""

from types import FrameType
from typing import List, Optional
from transitions import Machine, MachineError

from aux.timeout import Timeout
from hardware.button import Button
from hardware.buzzer import Buzzer
from hardware.led import LedStrip
from remote import NineLightRemote
from states import States
from constants import (
    BELL_REQUEST_TIMEOUT,
    PIN_LEDS,
    PIN_BUTTON,
    PIN_BUZZER,
    LEDS_TOTAL,
    LEDS_TOP,
    LEDS_BOTTOM
)


class NineLight:
    """Business logic class and state machine for our 9Light."""
    # pylint: disable=E1101

    def __init__(self):
        Machine(
            self,
            states=States,
            transitions=[
                # pylint: disable=C0301
                {"trigger": "none",    "source": "*",           "dest": States.NONE},       # noqa: E501
                {"trigger": "call",    "source": "*",           "dest": States.CALL},       # noqa: E501
                {"trigger": "video",   "source": "*",           "dest": States.VIDEO},      # noqa: E501
                {"trigger": "request", "source": States.VIDEO,  "dest": States.REQUEST},    # noqa: E501
                {"trigger": "request", "source": States.COFFEE, "dest": States.NONE},       # noqa: E501
                {"trigger": "coffee",  "source": States.NONE,   "dest": States.COFFEE}      # noqa: E501
            ],
            initial=States.NONE,
            after_state_change=self.on_state_changed
        )
        self.remotes: List[NineLightRemote] = []

        self._buzzer: Buzzer = Buzzer(PIN_BUZZER)
        self._button: Button = Button(PIN_BUTTON,
                                      callback_pressed=self.on_bell_button)
        self._leds: LedStrip = LedStrip(PIN_LEDS, LEDS_TOTAL, LEDS_TOP,
                                        LEDS_BOTTOM)
        self._bell_timeout: Optional[Timeout] = None

    def on_exit(self, _sig: Optional[int] = None,
                _frame: Optional[FrameType] = None) -> None:
        """Call GPIO cleanup routines."""
        self._button.cleanup()
        self._buzzer.cleanup()
        self._leds.cleanup()

    def get_state(self) -> str:
        """Get the current state as a lowercase string."""
        return str(self.state.name).lower()

    def set_state(self, target: str) -> bool:
        """Try to apply a new state."""
        try:
            self.trigger(target.lower())
        except MachineError:
            return False
        return True

    def add_remote(self, remote: NineLightRemote) -> None:
        """Add a new remote or update an existing one by IP."""
        self.delete_remote(remote)
        self.remotes.append(remote)

    def delete_remote(self, remote: NineLightRemote) -> None:
        """Remove an existing remote from the registration list by IP."""
        new_list = list(filter(lambda x: x.ip_addr != remote.ip_addr,
                               self.remotes))
        self.remotes = new_list

    def update_remotes(self) -> None:
        """Remove expired remotes."""
        new_list = filter(lambda x: not x.is_expired(), self.remotes)
        self.remotes = list(new_list)

    def send_update_to_remotes(self) -> None:
        """Send current status to all registered remotes."""
        for remote in self.remotes:
            remote.send_update(
                self.get_state(),
                [r.ip_addr for r in self.remotes]
            )

    def on_bell_button(self) -> None:
        """Trigger correct action when someone pushed the button."""
        if self.state == States.VIDEO:
            self.request()
        elif self.state == States.COFFEE:
            self.none()

    def on_state_changed(self) -> None:
        """Auto-called function triggered after any transition of the state
        machine."""
        self._leds.on_state_changed(self.state)
        if self._bell_timeout and self.state != States.REQUEST:
            self._bell_timeout.cancel()

    def on_enter_REQUEST(self) -> None:
        """Auto-called function triggered when entering the request state."""
        # pylint: disable=C0103
        self._buzzer.ring()
        self._bell_timeout = Timeout(self.video, BELL_REQUEST_TIMEOUT)
        self._bell_timeout.start()
