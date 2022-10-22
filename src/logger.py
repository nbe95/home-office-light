#!/usr/bin/env python3

"""Helper module for simple logger configuration."""

import logging
from dataclasses import dataclass
from datetime import datetime
from logging import DEBUG, Formatter, Logger, LogRecord, StreamHandler
from logging.handlers import BufferingHandler
from sys import stdout
from typing import List, Optional

from constants import LOG_BUFFER_CAPACITY, LOG_LEVEL


class MemoryLogBuffer(BufferingHandler):
    """Simple wrapper around logging.handlers.BufferingHandler, which allows us
    to grab log messages at runtime and e.g. show them on the frontend."""

    @dataclass
    class LogEntry:
        """Dataclass which holds one single log entry."""

        number: int
        time: datetime
        logger: str
        level: int
        path: str
        line: int
        message: str

    # Static list to hold messages from all loggers
    capacity: int = LOG_BUFFER_CAPACITY
    entry_count: int = 0
    entries: List[LogEntry] = []

    def __init__(self) -> None:
        BufferingHandler.__init__(self, self.capacity)
        self.setLevel(DEBUG)

    def flush(self) -> None:
        """Override flush method of BufferingHandler."""
        record: LogRecord
        for record in self.buffer:
            MemoryLogBuffer.add_entry(record)
        super().flush()

    def shouldFlush(self, record: LogRecord) -> bool:
        """Override shouldFlush method of BufferingHandler."""
        return True

    @staticmethod
    def add_entry(record: LogRecord) -> None:
        """Add a log entry to the static buffer and increment the counter."""
        MemoryLogBuffer.entry_count += 1
        MemoryLogBuffer.entries.append(
            MemoryLogBuffer.LogEntry(
                MemoryLogBuffer.entry_count,
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

    @staticmethod
    def get_entries(min_level: int = 0) -> List[LogEntry]:
        """Fetch all entries with a given minimum level in the buffer."""
        entries: List[MemoryLogBuffer.LogEntry] = list(
            filter(lambda x: x.level >= min_level, MemoryLogBuffer.entries)
        )
        return list(reversed(entries))

    @staticmethod
    def get_num_of_entries(
        level: Optional[int] = None, include_lower: bool = False
    ) -> int:
        """Fetch the number of all entries or, if set, all of them with a
        specified level in the buffer."""
        if level is None:
            return len(MemoryLogBuffer.entries)
        return sum(
            (
                entry.level >= level if include_lower
                else entry.level == level
            )
            for entry in MemoryLogBuffer.entries
        )



def get_logger(name: str, log_level: int = LOG_LEVEL) -> Logger:
    """Set up and return our desired logger."""
    logger: logging.Logger = logging.getLogger(name)

    memory_handler = MemoryLogBuffer()
    stdout_handler: StreamHandler = StreamHandler(stdout)
    stdout_handler.setFormatter(
        Formatter("%(levelname)s:%(name)s:%(message)s")
    )

    logger.setLevel(log_level)
    logger.addHandler(stdout_handler)
    logger.addHandler(memory_handler)

    return logger
