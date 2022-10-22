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
        if "new" in request.args:
            self.nl_instance.set_state(request.args["new"])

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
            start_time=self.nl_instance.start_time,
            state_changes=self.nl_instance.total_state_changes,
            num_remotes=len(self.nl_instance.remotes),
            port_backend=PORT_BACKEND,
            port_remote=PORT_REMOTE,
            current_state=self.nl_instance.get_state(),
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
        filter_name: str = request.args.get("filter", "").lower()
        if filter_name not in LOG_MAPPING:
            filter_name = "info"
        filter_level: int = LOG_MAPPING.get(filter_name, 0)

        return render_template(
            "log.html",
            navigation=self.navigation,
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            entries=MemoryLogBuffer.get_entries(filter_level),
            num_entries={
                "debug": MemoryLogBuffer.get_num_of_entries(DEBUG),
                "info": MemoryLogBuffer.get_num_of_entries(INFO),
                "warning": MemoryLogBuffer.get_num_of_entries(WARNING),
                "error": MemoryLogBuffer.get_num_of_entries(ERROR),
                "critical": MemoryLogBuffer.get_num_of_entries(CRITICAL),
            },
            num_entries_shown=MemoryLogBuffer.get_num_of_entries(
                filter_level, True
            ),
            num_entries_total=MemoryLogBuffer.get_num_of_entries(),
            num_entries_max=MemoryLogBuffer.capacity,
            filter=filter_level,
            filter_name=filter_name,
        )

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
