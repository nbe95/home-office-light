#!/usr/bin/env python3

"""9light frontend python module."""

from datetime import datetime
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from os.path import abspath
from typing import Dict, List, Optional, Tuple
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
from states import States

# pylint: disable=E1101


class Frontend:
    """Container for the frontend flask application."""

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
        self.app.jinja_options["extensions"] = [
            "jinja2_humanize_extension.HumanizeExtension"
        ]

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

    def generate_navigation(
        self,
    ) -> Dict[str, Tuple[List[str], Optional[Tuple[str, int]]]]:
        """Generate a dict containing all navigation items and badges."""

        num_warnings: int = MemoryLogBuffer.get_num_of_entries(
            WARNING, only_new=True
        )
        num_errors_critical: int = MemoryLogBuffer.get_num_of_entries(
            ERROR, only_new=True
        ) + MemoryLogBuffer.get_num_of_entries(CRITICAL, only_new=True)
        log_badge: Optional[Tuple[str, int]] = None
        if num_errors_critical > 0:
            log_badge = ("danger", num_errors_critical)
        elif num_warnings > 0:
            log_badge = ("warning", num_warnings)

        # link text, (URLs), (badge context, number)
        return {
            "State": (["/state", "/"], None),
            "Remotes": (
                ["/remotes"],
                (
                    "secondary",
                    len(list(filter(
                        lambda x: x.is_active(),
                        self.nl_instance.remotes,
                    ))),
                ),
            ),
            "Log": (["/log"], log_badge),
        }

    def state(self) -> str:
        """Renders the state page of the web application."""
        if "set" in request.args:
            self.nl_instance.set_state(request.args["set"])

        if "button" in request.args:
            self.nl_instance.on_bell_button()

        return render_template(
            "state.html",
            navigation=self.generate_navigation(),
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            hostname=HOSTNAME,
            ip_addr=IP_ADDR,
            sw_version=SW_VERSION,
            py_version=PY_VERSION,
            nl_instance=self.nl_instance,
            port_backend=PORT_BACKEND,
            port_remote=PORT_REMOTE,
            num_remotes_active=len(list(filter(
                lambda x: x.is_active(),
                self.nl_instance.remotes
            ))),
            num_remotes_inactive=len(list(filter(
                lambda x: not x.is_active(),
                self.nl_instance.remotes
            ))),
            state_mapping=(
                # name, text, icon, disabled
                ("none", "None", "fa-ban", False),
                ("call", "Call", "fa-phone", False),
                ("video", "Video", "fa-camera", False),
                (
                    "request",
                    "Request",
                    "fa-bell",
                    self.nl_instance.state != States.VIDEO,
                ),
                (
                    "coffee",
                    "I need a coffee…",
                    "fa-coffee",
                    self.nl_instance.state != States.NONE,
                ),
            ),
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

            elif "act-remote" in request.form:
                remote = NineLightRemote.parse_from_str(
                    request.form["act-remote"]
                )
                if remote:
                    self.nl_instance.activate_remote(remote)

            elif "deact-remote" in request.form:
                remote = NineLightRemote.parse_from_str(
                    request.form["deact-remote"]
                )
                if remote:
                    self.nl_instance.deactivate_remote(remote)

            elif "del-remote" in request.form:
                remote = NineLightRemote.parse_from_str(
                    request.form["del-remote"]
                )
                if remote:
                    self.nl_instance.delete_remote(remote)

        return render_template(
            "remotes.html",
            navigation=self.generate_navigation(),
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            client_ip=request.remote_addr,
            port_remote=PORT_REMOTE,
            remotes=list(enumerate(self.nl_instance.remotes)),
        )

    def log(self) -> str:
        """Renders the log page of the web application."""
        filter_name: str = (
            "info"
            if "filter" not in request.args
            else request.args["filter"].lower()
        )
        filter_level: int = INFO
        for level, properties in LOG_MAPPING.items():
            if properties[0].lower() == filter_name.lower():
                filter_level = level

        return render_template(
            "log.html",
            navigation=self.generate_navigation(),
            title=MAIN_TITLE,
            title_nav=MAIN_TITLE_NAVBAR,
            log_mapping=LOG_MAPPING,
            log_buffer=MemoryLogBuffer,
            filter_level=filter_level,
        )

    def run(self, port, host: str = "0.0.0.0") -> None:
        """Trigger the inner run method of the flask application."""
        self.app.run(host, port)
