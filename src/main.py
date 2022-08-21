#!/usr/bin/env python3

"""Main python module for 9light app.

This python module is the main entry point of the app and manages all internal
functionalities. It sets up a backend server for API access as well as a simple
web frontend for webbrowser based control.
"""

import signal
from threading import Thread

from nine_light import NineLight
from backend import Backend
from frontend import Frontend
from constants import (
    FRONTEND_TEMPLATE_DIR,
    FRONTEND_STATIC_DIR,
    PORT_FRONTEND,
    PORT_BACKEND
)


def main():
    """Execute the main app task."""
    # Create 9light object
    light = NineLight()

    # Set up backend thread
    backend: Backend = Backend(light)
    backend_thread: Thread = Thread(
        target=backend.run,
        args=(PORT_BACKEND,),
        daemon=True
    )
    backend_thread.start()

    # Set up frontend thread
    frontend: Frontend = Frontend(light, FRONTEND_TEMPLATE_DIR,
                                  FRONTEND_STATIC_DIR)
    frontend_thread: Thread = Thread(
        target=frontend.run,
        args=(PORT_FRONTEND,),
        daemon=True
    )
    frontend_thread.start()

    # Run until interrupted...
    signal.signal(signal.SIGTERM, light.on_exit)
    try:
        signal.pause()
    except KeyboardInterrupt:
        light.on_exit()


if __name__ == "__main__":
    main()
