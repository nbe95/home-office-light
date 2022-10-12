#!/usr/bin/env python3

"""Python module which handles 9light remotes."""

from datetime import datetime
from json import dumps
from socket import AF_INET, SOCK_STREAM, socket, timeout
from typing import List, Optional

from constants import PORT_REMOTE, REMOTE_EXP_TIMEOUT
from logger import get_logger

logger = get_logger(__name__)


class NineLightRemote:
    """Subclass for simple handling of 9light remotes."""

    def __init__(
        self,
        ip_addr: str,
        port: int = PORT_REMOTE,
        expiration: Optional[datetime] = None,
    ):
        self.ip_addr: str = ip_addr
        self.port: int = port
        self.skip_once: bool = False
        self.set_expiration(expiration)

        logger.debug("Remote with endpoint %s initialized.", self.ip_addr)

    def send_update(self, state: str, remotes: List[str]) -> None:
        """Send a HTTP request to the remote including the current 9light
        state."""
        # Skip if this very remote has triggered the state change
        if self.skip_once:
            logger.info("Skipping update for remote with endpoint %s.", self.ip_addr)
            self.skip_once = False
            return

        # The payload must be sent as one-line JSON string (with trailing \n)
        payload: str = dumps({"state": state, "remotes": remotes}, indent=None)
        http_request: str = (
            f"GET /remote HTTP/1.1\n" f"Host: {self.ip_addr}\n" "\n" f"{payload}\n"
        )
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((self.ip_addr, self.port))
            sock.sendall(http_request.encode("ascii"))
        except (timeout, ConnectionRefusedError) as err:
            logger.error(
                "Could not send status update to remote %s: %s", self.ip_addr, err
            )
        finally:
            sock.close()

    def set_expiration(self, expiration: Optional[datetime] = None) -> None:
        """Set the timestamp when this remote's registration will expire."""
        self.expiration: datetime = expiration or (datetime.now() + REMOTE_EXP_TIMEOUT)

        logger.debug(
            "Expiration for remote with endpoint %s set to %s.",
            self.ip_addr,
            self.expiration,
        )

    def is_expired(self) -> bool:
        """Check if this remote's registration is already expired."""
        return self.expiration <= datetime.now()
