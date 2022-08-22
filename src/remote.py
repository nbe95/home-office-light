#!/usr/bin/env python3

"""Python module which handles 9light remotes."""

from json import dumps
from datetime import datetime
from typing import Optional, List
from socket import socket, AF_INET, SOCK_STREAM

from constants import PORT_REMOTE, REMOTE_EXP_TIMEOUT


class NineLightRemote:
    """Subclass for simple handling of 9light remotes."""

    def __init__(self, ip_addr: str, port: int = PORT_REMOTE,
                 expiration: Optional[datetime] = None):
        self.ip_addr: str = ip_addr
        self.port: int = port
        self.skip_once: bool = False
        self.set_expiration(expiration)

    def send_update(self, state: str, remotes: List[str]) -> None:
        """Send a HTTP request to the remote including the current 9light
        state."""
        # Skip if this very remote has triggered the state change
        if self.skip_once:
            self.skip_once = False
            return

        payload: str = dumps({"state": state, "remotes": remotes})
        http_request: str = (f"GET /remote HTTP/2\n"
                             f"Host: {self.ip_addr}\n"
                             "\n"
                             f"{payload}\n")
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.ip_addr, self.port))
        sock.sendall(http_request.encode("utf-8"))
        sock.close()

    def set_expiration(self, expiration: Optional[datetime] = None) -> None:
        """Set the timestamp when this remote's registration will expire."""
        self.expiration: datetime = expiration or \
            (datetime.now() + REMOTE_EXP_TIMEOUT)

    def is_expired(self) -> bool:
        """Check if this remote's registration is already expired."""
        return self.expiration >= datetime.now()
