#!/usr/bin/env python3

"""9light frontend python module."""

from os.path import abspath
from re import match
from uuid import uuid4
from flask import Flask, render_template, request, Response
from typing import Optional

from nine_light import NineLight
from remote import NineLightRemote
from constants import (
    MAIN_TITLE,
    PORT_REMOTE
)


class Frontend:
    """Container for the frontend flask application."""

    def __init__(self, nl_instance: NineLight, template_folder: str, static_folder: str) -> None:
        Frontend.nl_instance: NineLight = nl_instance
        self.app: Flask = Flask(
            __name__,
            template_folder=abspath(template_folder),
            static_folder=abspath(static_folder)
        )
        self.app.secret_key: str = uuid4().hex

        @self.app.route("/", methods=["GET", "POST"])
        def _route_index():
            return Frontend.index()


    @staticmethod
    def index() -> str:
        """Returns the index page of the web application."""

        # Trigger actions if requested
        if request.method == "POST":
            if "set-state" in request.form:
                Frontend.nl_instance.set_state(request.form["new-state"])

            if "add-remote" in request.form:
                result = match("^((?:\d{1,3}\.){3}\d{1,3})(?:\:(\d+))?$", request.form["new-remote"])
                if result:
                    groups = result.groups()
                    ip: str = groups[0]
                    port: int = groups[1] or PORT_REMOTE
                    Frontend.nl_instance.add_remote(NineLightRemote(ip, port))

            if "del-remote" in request.form:
                Frontend.nl_instance.delete_remote(NineLightRemote(request.form["del-remote"], 0))

            if "bell-button" in request.form:
                if request.form["bell-button"] == "1":
                    Frontend.nl_instance.on_bell_button()

        return render_template("frontend.html",
            main_title=MAIN_TITLE,
            client_ip=request.remote_addr,
            current_state=Frontend.nl_instance.get_state(),
            remotes=enumerate(Frontend.nl_instance.remotes)
        )


    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
