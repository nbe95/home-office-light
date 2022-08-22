#!/usr/bin/env python3

"""9light backend python module."""

from uuid import uuid4
from typing import Optional
from flask import Flask, request, jsonify, Response

from nine_light import NineLight
from remote import NineLightRemote
from constants import (
    PORT_REMOTE
)

# pylint: disable=E1101


class Backend:
    """Container for the backend flask application."""

    def __init__(self, nl_instance: NineLight) -> None:
        self.nl_instance: NineLight = nl_instance
        self.app: Flask = Flask(__name__)
        self.app.secret_key = uuid4().hex

        @self.app.route("/state/get", methods=["GET"])
        def _state_get():
            return self.state()

        @self.app.route("/state/set", methods=["GET"])
        def _state_set():
            return self.state()

    def state(self) -> Response:
        """Gets the bare state of the system and - if provided - updates a
        remote registration."""

        if "remote" in request.args:
            self.nl_instance.add_remote(NineLightRemote(
                str(request.remote_addr),
                PORT_REMOTE
            ))

        new_state: Optional[str] = request.args.get("state")
        if new_state:
            self.nl_instance.set_state(new_state)

        return jsonify({
            "state": self.nl_instance.get_state(),
            "remotes": [r.ip_addr for r in self.nl_instance.remotes]
        })

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
