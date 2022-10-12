#!/usr/bin/env python3

"""9light frontend python module."""

from os.path import abspath
from re import match
from typing import Dict, List, Union, Any
from uuid import uuid4

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from constants import (
    MAIN_TITLE,
    MAIN_TITLE_NAVBAR,
    PORT_BACKEND,
    PORT_REMOTE,
    LOG_MAPPING,
)
from logger import MemoryLogBuffer
from nine_light import NineLight
from remote import NineLightRemote

# pylint: disable=E1101


class Frontend:
    """Container for the frontend flask application."""

    navigation: Dict[str, List[str]] = {
        "State": ["/state", "/"],
        "Remotes": ["/remotes"],
        "Events": ["/events"],
    }

    def __init__(
        self, nl_instance: NineLight, template_folder: str, static_folder: str
    ) -> None:
        self.nl_instance: NineLight = nl_instance
        self.app: Flask = Flask(
            __name__,
            template_folder=abspath(template_folder),
            static_folder=abspath(static_folder),
        )
        self.app.secret_key = uuid4().hex
        self.bootstrap: Bootstrap5 = Bootstrap5(self.app)

        @self.app.route("/", methods=["GET"])
        def _route_index():
            return self.state()

        @self.app.route("/state", methods=["GET"])
        def _route_state():
            return self.state()

        @self.app.route("/remotes", methods=["GET", "POST"])
        def _route_remotes():
            return self.remotes()

        @self.app.route("/events", methods=["GET"])
        def _route_events():
            return self.events()

    def state(self) -> str:
        """Renders the state page of the web application."""
        if "new" in request.args:
            self.nl_instance.set_state(request.args["new"])

        if "button" in request.args:
            self.nl_instance.on_bell_button()

        statistics: Dict[str, Any] = {
            "start_time": self.nl_instance.start_time,
            "state_changes": self.nl_instance.total_state_changes,
            "num_remotes": len(self.nl_instance.remotes),
            "listen_port": PORT_BACKEND,
            "remote_port": PORT_REMOTE,
        }

        return render_template(
            "state.html",
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            navigation=self.navigation,
            stat=statistics,
            current_state=self.nl_instance.get_state(),
        )

    def remotes(self) -> str:
        """Renders the remotes page of the web application."""
        if request.method == "POST":
            if "add-remote" in request.form:
                result = match(
                    r"^((?:\d{1,3}\.){3}\d{1,3})(?:\:(\d+))?$",
                    request.form["new-remote"],
                )
                if result:
                    groups = result.groups()
                    ip_addr: str = groups[0]
                    port: Union[str, int] = groups[1] or PORT_REMOTE
                    self.nl_instance.add_remote(
                        NineLightRemote(ip_addr, int(port))
                    )

            if "update-remotes" in request.form:
                self.nl_instance.update_remotes()

            if "del-remote" in request.form:
                self.nl_instance.delete_remote(
                    NineLightRemote(request.form["del-remote"], 0)
                )

        return render_template(
            "remotes.html",
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            navigation=self.navigation,
            client_ip=request.remote_addr,
            remotes=list(enumerate(self.nl_instance.remotes)),
        )

    def events(self) -> str:
        """Renders the events page of the web application."""
        filter_name: str = request.args.get("filter", "").upper()
        if filter_name not in LOG_MAPPING:
            filter_name = "DEBUG"
        filter_level: int = LOG_MAPPING.get(filter_name, 0)
        return render_template(
            "events.html",
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            navigation=self.navigation,
            events=MemoryLogBuffer.get_entries(filter_level),
            filter=filter_level,
            filter_name=filter_name,
        )

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
