
#!/usr/bin/env python3

"""Python module which handles 9Light remotes."""

from datetime import datetime, timedelta
from typing import Optional
from constants import (
    PORT_REMOTE,
    REMOTE_EXP_TIMEOUT_S
)


class NineLightRemote:
    """Subclass for simple handling of 9Light remotes."""
    def __init__(self,
                    ip: str,
                    port: int = PORT_REMOTE,
                    expiration: Optional[datetime] = None):
        self.ip: str = ip
        self.port: int = port
        self.set_expiration(expiration)

    def send_update(self, payload: str) -> None:
        """Send a HTTP request to the remote including the current 9Light state."""
        cmd: str = f"curl -fs -X GET \"http://{self.ip}:{self.port}/remote\" -d '{payload}' > /dev/null"
        subprocess.Popen(shlex.split(cmd))

    def set_expiration(self,
                        expiration: Optional[datetime] = None) -> None:
        """Set the timestamp when this remote's registration will expire."""
        self.expiration: datetime = expiration or datetime.now() + timedelta(seconds=REMOTE_EXP_TIMEOUT_S)

    def is_expired(self) -> bool:
        """Check if this remote's registration is already expired."""
        return self.expiration >= time()
