#!/bin/bash
GIT_VERSION="$(git describe --always --long --dirty --tags)" docker-compose up --build -d
