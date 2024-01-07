#!/usr/bin/env python3

"""Main python module for 9light app.

This python module is the main entry point of the app and manages all internal
functionalities. It sets up a backend server for API access as well as a simple
web frontend for webbrowser based control.
"""

import signal
from threading import Thread

from backend import Backend
from constants import (
    FRONTEND_STATIC_DIR,
    FRONTEND_TEMPLATE_DIR,
    PORT_BACKEND,
    PORT_FRONTEND,
)
from frontend import Frontend
from logger import get_logger
from nine_light import NineLight

logger = get_logger(__name__)


def main():
    """Execute the main app task."""
    logger.info("Starting main thread.")

    # Create 9light object
    light = NineLight()
    logger.debug("9light instance created.")

    # Set up backend thread
    backend: Backend = Backend(light)
    backend_thread: Thread = Thread(
        target=backend.run, args=(PORT_BACKEND,), daemon=True
    )
    backend_thread.start()
    logger.debug("Backend thread set up.")

    # Set up frontend thread
    frontend: Frontend = Frontend(
        light, FRONTEND_TEMPLATE_DIR, FRONTEND_STATIC_DIR
    )
    frontend_thread: Thread = Thread(
        target=frontend.run, args=(PORT_FRONTEND,), daemon=True
    )
    frontend_thread.start()
    logger.debug("Frontend thread set up.")

    # Run until interrupted...
    logger.info("Setup finished. Running until interrupted.")
    signal.signal(signal.SIGTERM, light.on_exit)
    try:
        signal.pause()
        logger.debug("SIGTERM triggered.")
    except KeyboardInterrupt:
        logger.debug("KeyboardInterrupt triggered.")
        light.on_exit()

    logger.info("Python script finished.")


if __name__ == "__main__":
    main()
