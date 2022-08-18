#!/usr/bin/env python3

"""Python module which handles the main 9light interfaces and functions."""

from transitions import Machine
from enum import Enum
from typing import List
from remote import NineLightRemote
from constants import (
    REMOTE_EXP_TIMEOUT_S,
    BELL_TIMEOUT_S
)


class NineLight:
    """Business logic class for our 9Light."""

    class States(Enum):
        """Enumeration of all available states with corresponding numerical ID."""
        NONE    = 0,
        CALL    = 1,
        VIDEO   = 2,
        REQUEST = 3,
        COFFEE  = 99

    def __init__(self):
        self.remotes: List[NineLightRemote] = []
        self.bell_timeout: Optional[Timeout] = None

        Machine(self,
            states=self.States,
            transitions=[
                { "trigger": "none",    "source": "*",                  "dest": self.States.NONE },
                { "trigger": "call",    "source": "*",                  "dest": self.States.CALL },
                { "trigger": "video",   "source": "*",                  "dest": self.States.VIDEO },
                { "trigger": "request", "source": self.States.VIDEO,    "dest": self.States.REQUEST },
                { "trigger": "request", "source": self.States.COFFEE,   "dest": self.States.NONE },
                { "trigger": "coffee",  "source": self.States.NONE,     "dest": self.States.COFFEE }
            ],
            initial=self.States.NONE,
            after_state_change=self.on_state_changed)

    def get_state(self) -> str:
        """Get the current state as a lowercase string."""
        return self.state.name.lower()

    def set_state(self, target: str) -> bool:
        """Try to apply a new state."""
        try:
            self.trigger(target)
        except:
            return False
        return True

    def add_remote(self, remote: NineLightRemote) -> None:
        """Add a new remote or update an existing one by IP."""
        new_list = list(filter(lambda x: x.ip != remote.ip, self.remotes))
        new_list.append(remote)
        self.remotes = new_list

    def delete_remote(self, remote: NineLightRemote) -> None:
        """Remove an existing remote from the registration list by IP."""
        new_list = list(filter(lambda x: x.ip != remote.ip, self.remotes))
        self.remotes = new_list

    def update_remotes(self) -> None:
        """Remove expired remotes."""
        new_list = filter(lambda x: not x.is_expired(), self.remotes)
        self.remotes = new_list

    def send_to_remotes(self, ignore: List[NineLightRemote]) -> None:
        payload: str = json.dumps({
            "state": parent.get_state(),
            "remotes": list(r.ip for r in parent.remotes)
        })
        for remote in filter(lambda x: x not in ignore, self.remotes):
            remote.send_update(payload)

    def on_state_changed(self) -> None:
        # self.leds.set_mode(self.state)

        # Cancel bell timeout if leaving e.g. request state
        if self.bell_timeout:
            self.bell_timeout.canceled = True

    def on_enter_REQUEST(self) -> None:
        #self.bell.ring()
        self.bell_timeout = Timeout(self.video, BELL_TIMEOUT_S)
