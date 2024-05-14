#!/usr/bin/env python3.8
# coding:utf-8
# Copyright (C) 2019-2022 All rights reserved.
# FILENAME:  logger.py
# VERSION: 	 0.5
# CREATED: 	 2020-11-30 14:24
# AUTHOR: 	 Sitt Guruvanich <aekasitt.g@siamintech.co.th>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""
Module defining class Logger
"""
### Standard Packages ###
import re
import sys
from logging import (
    Filter,
    Formatter,
    INFO,
    LogRecord,
    StreamHandler,
    getLogger,
    FileHandler,
)
from typing import Any, Dict

# Define Color Escape Codes for Logging
BLUE: str = "\033[1;94m"  # Sky Blue ANSI Escape Code
CYAN: str = "\033[1;36m"  # Light Cyan ANSI Escape Code
GREEN: str = "\033[1;92m"  # Green ANSI Escape Code
NC: str = "\033[1;0m"  # No Colour ANSI Escape Code
RED: str = "\033[1;31m"  # Red ANSI Escape Code
YELLOW: str = "\033[1;93m"  # Yellow ANSI Escape Code
ColorEnum: Dict[str, str] = {
    "blue": BLUE,
    "cyan": CYAN,
    "green": GREEN,
    "red": RED,
    "yellow": YELLOW,
}


class CleanAnsiFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        if hasattr(record, "clean_message"):
            record.msg = record.clean_message
        return super().format(record)


class CleanAnsiFilter(Filter):
    # 7-bit C1 ANSI sequences
    ANSI_ESCAPE = re.compile(
        r"""
      \x1B  # ESC
      (?:   # 7-bit C1 Fe (except CSI)
          [@-Z\\-_]
      |     # or [ for CSI, followed by a control sequence
          \[
          [0-?]*  # Parameter bytes
          [ -/]*  # Intermediate bytes
          [@-~]   # Final byte
      )
  """,
        re.VERBOSE,
    )

    def clean_ansi(self, message: str) -> str:
        if message is None:
            return ""
        return CleanAnsiFilter.ANSI_ESCAPE.sub("", str(message))

    def filter(self, record: LogRecord) -> bool:
        record.clean_message = self.clean_ansi(
            record.msg)  # type: ignore[attr-defined]
        return True


class Logger(object):
    """Class used Log to sys.stdout"""

    def __init__(self, log_name: str, save_log: bool = True):
        self.logger = getLogger(log_name)
        self.logger.addFilter(CleanAnsiFilter())

        ### Logs to Stream ###
        handler: StreamHandler = StreamHandler(sys.stdout)
        fmt: Formatter = Formatter(
            f"%(asctime)s {CYAN}[%(levelname)s]{NC} %(message)s")
        handler.setFormatter(fmt)
        self.logger.addHandler(handler)
        self.logger.setLevel(INFO)

        # Logs to File
        if save_log:
            file_name = f"logs/{log_name}.log"
            file_handler = FileHandler(file_name)
            file_filter = CleanAnsiFilter()  # Create a filter instance for file handler
            file_handler.addFilter(
                file_filter
            )  # Add filter to remove ANSI escape codes from log file
            file_formatter = CleanAnsiFormatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            )  # Use the custom formatter

            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def __del__(self) -> None:
        """
        Release all of Logger handlers and then release Logger instance.
        """
        try:
            for handler in list(self.logger.handlers):
                # self.logger.removeHandler(handler)
                del handler
            if self.logger is not None:
                del self.logger
        except AttributeError:
            pass

    def info(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with severity 'INFO' on the root logger. If the logger has
        no handlers, call basicConfig() to add a console handler with a pre-defined
        format.
        """
        if len(args) > 0:
            args_dict: Dict[str, Any] = args[0]
            color = args_dict.get("color", None)
            if color is not None:
                color = ColorEnum.get(color, NC)
                msg = f"{color}{msg}{NC}"
                args = args[1:]
        self.logger.info(msg, *args, **kwargs)

    def success(self, msg: object, *args: Any, **kwargs: Any) -> None:
        args += (dict(color="green"),)
        self.info(msg, *args, **kwargs)

    def warn(self, msg: object, *args: Any, **kwargs: Any) -> None:
        args += (dict(color="yellow"),)
        self.info(msg, *args, **kwargs)

    def safe(self, msg: object, *args: Any, **kwargs: Any) -> None:
        args += (dict(color="blue"),)
        self.info(msg, *args, **kwargs)

    def danger(self, msg: object, *args: Any, **kwargs: Any) -> None:
        args += (dict(color="red"),)
        self.info(msg, *args, **kwargs)

    # When a method is not found, shortcuts it to instance's `logger` member's Method
    def __getattr__(self, name: str) -> Any:
        return getattr(self.logger, name)
