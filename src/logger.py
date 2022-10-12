#!/usr/bin/env python3

"""Helper module for simple logger configuration."""

import logging
from dataclasses import dataclass
from datetime import datetime
from logging import DEBUG, Filter, Formatter, Logger, LogRecord, StreamHandler
from logging.handlers import BufferingHandler
from sys import stdout
from typing import List

from constants import LOG_BUFFER_CAPACITY, LOG_LEVEL


class MemoryLogBuffer(BufferingHandler):
    """Simple wrapper around logging.handlers.BufferingHandler, which allows us
    to grab log messages at runtime and e.g. show them on the frontend."""

    @dataclass
    class LogEntry:
        time: datetime
        logger: str
        level: int
        path: str
        line: int
        message: str

    # Static list to hold messages from all loggers
    capacity: int = LOG_BUFFER_CAPACITY
    entries: List[LogEntry] = []

    def __init__(self) -> None:
        BufferingHandler.__init__(self, self.capacity)
        self.setLevel(DEBUG)

    def flush(self) -> None:
        record: LogRecord
        for record in self.buffer:
            MemoryLogBuffer.entries.append(
                MemoryLogBuffer.LogEntry(
                    datetime.fromtimestamp(record.created),
                    record.name,
                    record.levelno,
                    record.pathname,
                    record.lineno,
                    record.message,
                )
            )
            MemoryLogBuffer.entries = MemoryLogBuffer.entries[
                -MemoryLogBuffer.capacity :
            ]
        super().flush()

    def shouldFlush(self, record: LogRecord) -> bool:
        return True

    @staticmethod
    def get_entries() -> List[LogEntry]:
        return MemoryLogBuffer.entries


def get_logger(name: str, log_level: int = LOG_LEVEL) -> Logger:
    """Set up and return our desired logger."""
    logger: logging.Logger = logging.getLogger(name)

    memory_handler = MemoryLogBuffer()
    stdout_handler: StreamHandler = StreamHandler(stdout)
    stdout_handler.setFormatter(Formatter("%(levelname)s:%(name)s:%(message)s"))

    logger.setLevel(log_level)
    logger.addHandler(stdout_handler)
    logger.addHandler(memory_handler)

    return logger
