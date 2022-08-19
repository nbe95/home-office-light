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
    nl_instance: NineLight

    def __init__(self, nl_instance: NineLight) -> None:
        Backend.nl_instance = nl_instance
        self.app: Flask = Flask(__name__)
        self.app.secret_key = uuid4().hex

        @self.app.route("/status/get", methods=["GET"])
        def _status_get():
            return Backend.status()

        @self.app.route("/status/set", methods=["GET"])
        def _status_set():
            return Backend.status()

    @staticmethod
    def status() -> Response:
        """Gets the bare status of the system and - if provided - updates a
        remote registration."""

        if "remote" in request.args:
            Backend.nl_instance.add_remote(NineLightRemote(
                str(request.remote_addr),
                PORT_REMOTE
            ))

        new_state: Optional[str] = request.args.get("status")
        if new_state:
            Backend.nl_instance.set_state(new_state)

        return jsonify({
            "state": Backend.nl_instance.get_state(),
            "remotes": [r.ip_addr for r in Backend.nl_instance.remotes]
        })

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
