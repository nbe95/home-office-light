#!/usr/bin/env python3

"""Main python module for 9light app.

This python module is the main entry point of the app and manages all internal
functionalities. It sets up a backend server for API access as well as a simple
web frontend for webbrowser based control.
"""

from nine_light import NineLight
from frontend import Frontend
from constants import (
    FRONTEND_TEMPLATE_DIR,
    FRONTEND_STATIC_DIR,
    PORT_FRONTEND,
    PORT_BACKEND,
    PORT_REMOTE
)


def main():
    """Execute the main app task."""
    # Create 9light object
    nl = NineLight()

    # Set up backend API
    # backend: Backend = Backend(nl, )
    # backend.run(PORT_BACKEND)

    # Set up web frontend
    frontend: Frontend = Frontend(nl, FRONTEND_TEMPLATE_DIR, FRONTEND_STATIC_DIR)
    frontend.run(PORT_FRONTEND)


if __name__ == "__main__":
    main()
