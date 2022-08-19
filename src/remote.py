#!/usr/bin/env python3

"""Python module which handles 9light remotes."""

from datetime import datetime
from requests import request
from typing import Optional, List

from constants import PORT_REMOTE, REMOTE_EXP_TIMEOUT


class NineLightRemote:
    """Subclass for simple handling of 9light remotes."""

    def __init__(self, ip: str, port: int = PORT_REMOTE,
                 expiration: Optional[datetime] = None):
        self.ip: str = ip
        self.port: int = port
        self.set_expiration(expiration)

    def send_update(self, state: str, remotes: List[str]) -> None:
        """Send a HTTP request to the remote including the current 9light
        state."""
        # Skip if this very remote has triggered the state change
        if self.skip_once:
            self.skip_once = False
            return

        # cmd: str = f"curl -fs -X GET \"http://{self.ip}:{self.port}/remote\" -d '{payload}' > /dev/null"
        # subprocess.Popen(shlex.split(cmd))
        request(
            "GET",
            f"http://{self.ip}:{self.port}/remote",
            headers={"state": state, "remotes": remotes},
        )

    def set_expiration(self, expiration: Optional[datetime] = None) -> None:
        """Set the timestamp when this remote's registration will expire."""
        self.expiration: datetime = expiration or \
            (datetime.now() + REMOTE_EXP_TIMEOUT)

    def is_expired(self) -> bool:
        """Check if this remote's registration is already expired."""
        return self.expiration >= datetime.now()
