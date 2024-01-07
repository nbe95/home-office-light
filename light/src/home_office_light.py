#!/usr/bin/env python3

"""Python module which handles the main HomeOfficeLight interfaces and functions."""

from datetime import datetime
from types import FrameType
from typing import List, Optional

from transitions import Machine, MachineError

from aux.timeout import Timeout
from constants import (
    BELL_REQUEST_TIMEOUT,
    LEDS_BOTTOM,
    LEDS_TOP,
    LEDS_TOTAL,
    PIN_BUTTON,
    PIN_BUZZER,
    PIN_LEDS,
)
from hardware.button import Button
from hardware.buzzer import Buzzer
from hardware.led import LedStrip
from logger import get_logger
from remote import HomeOfficeLightRemote
from states import States

logger = get_logger(__name__)


class HomeOfficeLight:
    """Business logic class and state machine for our HomeOfficeLight."""

    # pylint: disable=E1101

    def __init__(self):
        logger.debug("Initializing state machine.")
        Machine(
            self,
            states=States,
            transitions=[
                # pylint: disable=C0301
                {
                    "trigger": "none",
                    "source": "*",
                    "dest": States.NONE,
                },  # noqa: E501
                {
                    "trigger": "call",
                    "source": "*",
                    "dest": States.CALL,
                },  # noqa: E501
                {
                    "trigger": "video",
                    "source": "*",
                    "dest": States.VIDEO,
                },  # noqa: E501
                {
                    "trigger": "request",
                    "source": States.VIDEO,
                    "dest": States.REQUEST,
                },  # noqa: E501
                {
                    "trigger": "request",
                    "source": States.COFFEE,
                    "dest": States.NONE,
                },  # noqa: E501
                {
                    "trigger": "coffee",
                    "source": States.NONE,
                    "dest": States.COFFEE,
                },  # noqa: E501
            ],
            initial=States.NONE,
            after_state_change=self.on_state_changed,
        )

        self.start_time: datetime = datetime.now()
        self.total_state_changes: int = 0
        self.remotes: List[HomeOfficeLightRemote] = []

        self._buzzer: Buzzer = Buzzer(PIN_BUZZER)
        self._button: Button = Button(
            PIN_BUTTON, callback_pressed=self.on_bell_button
        )
        self._leds: LedStrip = LedStrip(
            PIN_LEDS, LEDS_TOTAL, LEDS_TOP, LEDS_BOTTOM
        )
        self._bell_timeout: Optional[Timeout] = None

        logger.debug("HomeOfficeLight instance initialized.")

    def on_exit(
        self, _sig: Optional[int] = None, _frame: Optional[FrameType] = None
    ) -> None:
        """Call GPIO cleanup routines."""
        logger.info("Running cleanup routine.")

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

    def on_remote_request(
        self, remote: HomeOfficeLightRemote, incr_tx: bool = False
    ) -> None:
        """Perform actions when an incoming remote request is recognized."""
        self.add_or_update_remote(remote)
        if remote in self.remotes:
            index: int = self.remotes.index(remote)
            self.remotes[index].skip_once = True
            self.remotes[index].rx_count += 1
            if incr_tx:
                self.remotes[index].tx_count += 1

    def get_remote(self, remote: HomeOfficeLightRemote) -> Optional[HomeOfficeLightRemote]:
        """Fetch the actual remote object by passing a reference object with
        matching IP and port."""
        return next(filter(lambda x: x == remote, self.remotes), None)

    def add_or_update_remote(self, remote: HomeOfficeLightRemote) -> None:
        """Add a new remote or update an existing one."""
        act_remote: Optional[HomeOfficeLightRemote] = self.get_remote(remote)
        if act_remote:
            act_remote.set_timestamp(datetime.now())

        else:
            remote.set_timestamp(datetime.now())
            self.remotes.append(remote)
            logger.info("%s registered.", remote)

    def delete_remote(self, remote: HomeOfficeLightRemote) -> None:
        """Remove an existing remote from the registration list."""
        if remote in self.remotes:
            self.remotes.remove(remote)
            logger.info("%s removed.", remote)

    def activate_remote(self, remote: HomeOfficeLightRemote) -> None:
        """Activate an existing remote from the registration list."""
        act_remote: Optional[HomeOfficeLightRemote] = self.get_remote(remote)
        if act_remote:
            act_remote.set_timestamp(datetime.now())
            logger.info("%s activated.", remote)

    def deactivate_remote(self, remote: HomeOfficeLightRemote) -> None:
        """Deactivate an existing remote from the registration list."""
        act_remote: Optional[HomeOfficeLightRemote] = self.get_remote(remote)
        if act_remote:
            act_remote.set_timestamp(None)
            logger.info("%s deactivated.", remote)

    def send_update_to_remotes(self) -> None:
        """Send the current state to all active remotes."""
        for remote in self.remotes:
            remote.send_update(self.get_state(), self.remotes)

    def on_bell_button(self) -> None:
        """Trigger correct action when someone pushed the button."""
        logger.info("Bell button triggered.")

        if self.state == States.VIDEO:
            self.request()
        elif self.state == States.COFFEE:
            self.none()

    def on_state_changed(self) -> None:
        """Auto-called function triggered after any transition of the state
        machine."""
        logger.info("HomeOfficeLight state changed to %s.", self.get_state().upper())
        self.total_state_changes += 1

        # Control LED strip
        self._leds.on_state_changed(self.state)

        # Trigger bell
        if self._bell_timeout and self.state != States.REQUEST:
            self._bell_timeout.cancel()

        # Update remotes
        self.send_update_to_remotes()

    def on_enter_REQUEST(self) -> None:
        """Auto-called function triggered when entering the request state."""
        # pylint: disable=C0103
        self._buzzer.ring()
        self._bell_timeout = Timeout(self.video, BELL_REQUEST_TIMEOUT)
        self._bell_timeout.start()
