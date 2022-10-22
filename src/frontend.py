#!/usr/bin/env python3

"""9light frontend python module."""

from os.path import abspath
from typing import Dict, List, Optional
from uuid import uuid4

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from constants import (
    HOSTNAME,
    IP_ADDR,
    LOG_MAPPING,
    MAIN_TITLE,
    MAIN_TITLE_NAVBAR,
    PORT_BACKEND,
    PORT_REMOTE,
    PY_VERSION,
    SW_VERSION,
)
from logger import MemoryLogBuffer
from nine_light import NineLight
from remote import NineLightRemote
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from states import States

# pylint: disable=E1101


class Frontend:
    """Container for the frontend flask application."""

    navigation: Dict[str, List[str]] = {
        "State": ["/state", "/"],
        "Remotes": ["/remotes"],
        "Log": ["/log"],
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

        @self.app.route("/log", methods=["GET"])
        def _route_log():
            return self.log()

    def state(self) -> str:
        """Renders the state page of the web application."""
        if "set" in request.args:
            self.nl_instance.set_state(request.args["set"])

        if "button" in request.args:
            self.nl_instance.on_bell_button()

        return render_template(
            "state.html",
            navigation=self.navigation,
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            hostname=HOSTNAME,
            ip_addr=IP_ADDR,
            sw_version=SW_VERSION,
            py_version=PY_VERSION,
            nl_instance=self.nl_instance,
            port_backend=PORT_BACKEND,
            port_remote=PORT_REMOTE,
            state_mapping=(
                # name, text, icon, disabled
                ("none", "None", "fa-ban", False),
                ("call", "Call", "fa-phone", False),
                ("video", "Video", "fa-camera", False),
                ("request", "Request", "fa-bell", self.nl_instance.state != States.VIDEO),
                ("coffee", "I need a coffee…", "fa-coffee", self.nl_instance.state != States.NONE),
            )
        )

    def remotes(self) -> str:
        """Renders the remotes page of the web application."""
        if request.method == "POST":
            remote: Optional[NineLightRemote]
            if "add-remote" in request.form:
                remote = NineLightRemote.parse_from_str(
                    request.form["new-remote"]
                )
                if remote:
                    self.nl_instance.add_or_update_remote(remote)

            if "del-remote" in request.form:
                remote = NineLightRemote.parse_from_str(
                    request.form["del-remote"]
                )
                if remote:
                    self.nl_instance.delete_remote(remote)

            if "update-remotes" in request.form:
                self.nl_instance.remove_expired_remotes()

        return render_template(
            "remotes.html",
            navigation=self.navigation,
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            client_ip=request.remote_addr,
            remotes=list(enumerate(self.nl_instance.remotes)),
        )

    def log(self) -> str:
        """Renders the log page of the web application."""
        filter_name: str = (
            "info" if "filter" not in request.args
            else request.args["filter"].lower()
        )
        filter_level: int = INFO
        for level, properties in LOG_MAPPING.items():
            if properties[0].lower() == filter_name.lower():
                filter_level = level

        return render_template(
            "log.html",
            navigation=self.navigation,
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            log_mapping=LOG_MAPPING,
            log_buffer=MemoryLogBuffer,
            filter_level=filter_level,
        )

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
