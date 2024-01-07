#!/usr/bin/env python3

"""Python module which handles HomeOfficeLight remotes."""

from datetime import datetime
from json import dumps
from re import match
from socket import AF_INET, SOCK_STREAM, socket, timeout
from typing import List, Optional, Union

from constants import PORT_REMOTE, REMOTE_EXP_TIMEOUT
from logger import get_logger

logger = get_logger(__name__)


class HomeOfficeLightRemote:
    """Subclass for simple handling of HomeOfficeLight remotes."""

    _SOCKET_TIMEOUT_SEC: int = 1

    def __init__(
        self, ip_addr: str, port: int = PORT_REMOTE, skip_once: bool = False
    ) -> None:
        self.ip_addr: str = ip_addr
        self.port: int = port
        self.skip_once: bool = skip_once
        self.rx_count: int = 0
        self.tx_count: int = 0
        self.tx_errors: int = 0
        self.last_contact: Optional[datetime]

        logger.debug("%s initialized.", self)

    @staticmethod
    def parse_from_str(
        remote_str: str, default_port: int = PORT_REMOTE
    ) -> Optional["HomeOfficeLightRemote"]:
        """Parse a string consisting of an IP address and a port (optional) and
        creates a remote object.
        Example: '192.168.0.42' or '192.168.0.69:1234'."""

        result = match(r"^((?:\d{1,3}\.){3}\d{1,3})(?:\:(\d+))?$", remote_str)
        if not result:
            return None

        groups = result.groups()
        ip_addr: str = groups[0]
        port: Union[str, int] = groups[1] or default_port
        return HomeOfficeLightRemote(ip_addr, int(port))

    def send_update(
        self, state_str: str, remotes: List["HomeOfficeLightRemote"]
    ) -> None:
        """Send a HTTP request to the remote including the current HomeOfficeLight
        state."""
        # Skip if this remote has triggered the state change or is disabled
        if not self.is_active():
            return

        if self.skip_once:
            logger.debug("Skipping update for %s once.", self)
            self.skip_once = False
            return

        # The payload must be sent as one-line JSON string (with trailing \n)
        payload: str = dumps(
            {
                "state": state_str,
                "remotes": [remote.ip_addr for remote in remotes],
            },
            indent=None,
        )
        http_request: str = (
            f"GET /remote HTTP/1.1\n"
            f"Host: {self.ip_addr}\n"
            "\n"
            f"{payload}\n"
        )
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(self._SOCKET_TIMEOUT_SEC)
        try:
            sock.connect((self.ip_addr, self.port))
            sock.sendall(http_request.encode("ascii"))
            logger.info("State update sent to %s.", self)

        except (timeout, ConnectionRefusedError) as err:
            logger.error("Could not send status update to %s (%s).", self, err)
            self.tx_errors += 1

        finally:
            sock.close()
            self.tx_count += 1

    def set_timestamp(self, last_contact: Optional[datetime]) -> None:
        """Set the timestamp of this remote's last contact with us."""
        self.last_contact = last_contact
        logger.debug("Timestamp for %s set to %s.", self, self.last_contact)

    def is_active(self) -> bool:
        """Check if this remote's registration is expired."""
        return (
            False
            if self.last_contact is None
            else self.last_contact + REMOTE_EXP_TIMEOUT >= datetime.now()
        )

    def __repr__(self) -> str:
        """Overload repr operator for a serialized representation for debugging
        purposes."""
        return f"HomeOfficeLightRemote({self.ip_addr}, {self.port})"

    def __str__(self) -> str:
        """Overload str operator for a serialized representation."""
        return f"Remote {self.ip_addr}:{self.port}"

    def __eq__(self, other: object) -> bool:
        """Compare remotes by IP address and port only."""
        if not isinstance(other, HomeOfficeLightRemote):
            return NotImplemented
        return self.ip_addr == other.ip_addr and self.port == other.port
