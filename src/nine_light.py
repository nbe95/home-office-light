#!/usr/bin/env python3

"""Python module which handles the main 9light interfaces and functions."""

from enum import Enum
from typing import List, Optional
from transitions import Machine

# from bell import Bell
# from led import LedStrip
from remote import NineLightRemote
from timeout import Timeout
from constants import BELL_REQUEST_TIMEOUT

# pylint: disable=E1101

class NineLight:
    """Business logic class and state machine for our 9Light."""

    class States(Enum):
        """Enumeration of all states with corresponding numerical ID."""
        NONE = 0
        CALL = 1
        VIDEO = 2
        REQUEST = 3
        COFFEE = 99

    def __init__(self):
        self.remotes: List[NineLightRemote] = []
        self._leds: LedStrip = LedStrip(PIN_LEDS, LEDS_TOTAL, LEDS_TOP,
                                        LEDS_BOTTOM)
        self._bell: Bell = Bell(PIN_BUTTON, PIN_BUZZER)
        self._bell_timeout: Optional[Timeout] = None

        Machine(self,
                states=self.States,
                transitions=[
                    # pylint: disable=C0301
                    {"trigger": "none",    "source": "*",                  "dest": self.States.NONE},       # noqa: E501
                    {"trigger": "call",    "source": "*",                  "dest": self.States.CALL},       # noqa: E501
                    {"trigger": "video",   "source": "*",                  "dest": self.States.VIDEO},      # noqa: E501
                    {"trigger": "request", "source": self.States.VIDEO,    "dest": self.States.REQUEST},    # noqa: E501
                    {"trigger": "request", "source": self.States.COFFEE,   "dest": self.States.NONE},       # noqa: E501
                    {"trigger": "coffee",  "source": self.States.NONE,     "dest": self.States.COFFEE}      # noqa: E501
                ],
                initial=self.States.NONE,
                after_state_change=self.on_state_changed)

    def get_state(self) -> str:
        """Get the current state as a lowercase string."""
        return self.state.name.lower()

    def set_state(self, target: str) -> bool:
        """Try to apply a new state."""
        try:
            self.trigger(target.lower())
        except KeyboardInterrupt:
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
        if self.state == NineLight.States.VIDEO:
            self.request()
        elif self.state == NineLight.States.COFFEE:
            self.none()

    def on_state_changed(self) -> None:
        """Auto-called function triggered after any transition of the state
        machine."""
        self._leds.on_state_changed(self.state)

        # Cancel bell timeout if leaving e.g. request state
        if self._bell_timeout:
            self._bell_timeout.cancel()

    def on_enter_REQUEST(self) -> None:
        """Auto-called function triggered when entering the request state."""
        # pylint: disable=C0103
        self._bell.ring()
        self._bell_timeout = Timeout(self.video, BELL_REQUEST_TIMEOUT)

    def cleanup(self) -> None:
        """Cleanup function for GPIO handling."""
        self._bell.cleanup()
