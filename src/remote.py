#!/usr/bin/env python3

"""Python module which handles 9light remotes."""

import logging
from json import dumps
from datetime import datetime
from typing import Optional, List
from socket import socket, timeout, AF_INET, SOCK_STREAM

from constants import (
    LOG_LEVEL,
    PORT_REMOTE,
    REMOTE_EXP_TIMEOUT
)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class NineLightRemote:
    """Subclass for simple handling of 9light remotes."""

    def __init__(self, ip_addr: str, port: int = PORT_REMOTE,
                 expiration: Optional[datetime] = None):
        self.ip_addr: str = ip_addr
        self.port: int = port
        self.skip_once: bool = False
        self.set_expiration(expiration)

        logger.debug("Remote with endpoint %s:%d initialized.", self.ip_addr,
                     self.port)

    def send_update(self, state: str, remotes: List[str]) -> None:
        """Send a HTTP request to the remote including the current 9light
        state."""
        # Skip if this very remote has triggered the state change
        if self.skip_once:
            logger.info("Skipping update for remote with endpoint %s:%d.",
                        self.ip_addr, self.port)
            self.skip_once = False
            return

        # The payload must be sent as one-line JSON string (with trailing \n)
        payload: str = dumps({"state": state, "remotes": remotes}, indent=None)
        http_request: str = (f"GET /remote HTTP/1.1\n"
                             f"Host: {self.ip_addr}\n"
                             "\n"
                             f"{payload}\n")
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((self.ip_addr, self.port))
            sock.sendall(http_request.encode("ascii"))
        except (timeout, ConnectionRefusedError) as err:
            logging.error("Could not send status update to remote %s:%d: %s",
                          self.ip_addr, self.port, err)
        finally:
            sock.close()

    def set_expiration(self, expiration: Optional[datetime] = None) -> None:
        """Set the timestamp when this remote's registration will expire."""
        self.expiration: datetime = expiration or \
            (datetime.now() + REMOTE_EXP_TIMEOUT)

        logger.debug("Expiration for remote with endpoint %s:%d set to %s.",
                     self.ip_addr, self.port, self.expiration)

    def is_expired(self) -> bool:
        """Check if this remote's registration is already expired."""
        return self.expiration >= datetime.now()
