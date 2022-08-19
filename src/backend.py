#!/usr/bin/env python3

"""9light backend python module."""

from uuid import uuid4
from flask import Flask, request, jsonify
from typing import Optional

from nine_light import NineLight
from remote import NineLightRemote
from constants import (
    PORT_REMOTE
)


class Backend:
    """Container for the backend flask application."""

    def __init__(self, nl_instance: NineLight) -> None:
        Backend.nl_instance: NineLight = nl_instance
        self.app: Flask = Flask(__name__)
        self.app.secret_key: str = uuid4().hex

        @self.app.route("/status/get", methods=["GET"])
        def _status_get():
            return Backend.status()

        @self.app.route("/status/set", methods=["GET"])
        def _status_set():
            return Backend.status()

    @staticmethod
    def status() -> str:
        """Gets the bare status of the system and - if provided - updates a
        remote registration."""

        if "remote" in request.args:
            Backend.nl_instance.add_remote(NineLightRemote(
                request.remote_addr,
                PORT_REMOTE
            ))

        new_state: Optional[str] = request.args.get("status")
        if new_state:
            Backend.nl_instance.set_state(new_state)

        return jsonify({
            "state": Backend.nl_instance.get_state(),
            "remotes": [r.ip for r in Backend.nl_instance.remotes]
        })

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
