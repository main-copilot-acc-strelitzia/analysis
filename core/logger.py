"""Structured logging for the Strelitzia Trader application with verbosity control."""

import logging
import sys
from datetime import datetime
from typing import Optional
from enum import Enum


class LogVerbosity(Enum):
    """Logging verbosity levels."""
    MINIMAL = 0      # Only CRITICAL and ERROR
    STANDARD = 1     # WARNING, ERROR, CRITICAL
    VERBOSE = 2      # All including INFO
    DEBUG = 3        # All including DEBUG


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.msg = f"{color}{record.getMessage()}{self.RESET}"
        return super().format(record)


class Logger:
    """Centralized logging manager with runtime verbosity control."""

    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    _verbosity: LogVerbosity = LogVerbosity.STANDARD
    _console_handler: Optional[logging.StreamHandler] = None
    _file_handler: Optional[logging.FileHandler] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the logger with handlers."""
        self._logger = logging.getLogger('StrelitziaTrader')
        self._logger.setLevel(logging.DEBUG)

        # Console handler
        self._console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._console_handler.setFormatter(console_formatter)

        # File handler
        self._file_handler = logging.FileHandler('strelitzia_trader.log')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(file_formatter)
        self._file_handler.setLevel(logging.DEBUG)

        self._logger.addHandler(self._console_handler)
        self._logger.addHandler(self._file_handler)
        
        # Set initial verbosity
        self.set_verbosity(LogVerbosity.STANDARD)

    def set_verbosity(self, verbosity: LogVerbosity) -> None:
        """
        Set logging verbosity level.
        
        Can be changed at runtime without restarting app.
        
        Args:
            verbosity: LogVerbosity level
        """
        self._verbosity = verbosity
        
        # Map verbosity to console log level
        level_map = {
            LogVerbosity.MINIMAL: logging.CRITICAL,
            LogVerbosity.STANDARD: logging.WARNING,
            LogVerbosity.VERBOSE: logging.INFO,
            LogVerbosity.DEBUG: logging.DEBUG,
        }
        
        if self._console_handler:
            self._console_handler.setLevel(level_map[verbosity])
        
        self._logger.info(f"Logging verbosity set to {verbosity.name}")

    def get_verbosity(self) -> LogVerbosity:
        """Get current logging verbosity level."""
        return self._verbosity

    def debug(self, message: str, *args):
        """Log debug message."""
        self._logger.debug(message, *args)

    def info(self, message: str, *args):
        """Log info message."""
        self._logger.info(message, *args)

    def warning(self, message: str, *args):
        """Log warning message."""
        self._logger.warning(message, *args)

    def error(self, message: str, *args):
        """Log error message."""
        self._logger.error(message, *args)

    def exception(self, message: str, *args):
        """Log an exception with traceback."""
        self._logger.exception(message, *args)

    def critical(self, message: str, *args):
        """Log critical message."""
        self._logger.critical(message, *args)

    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self._logger

    @classmethod
    def get_instance(cls) -> 'Logger':
        """Get singleton Logger instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_logger() -> Logger:
    """Get the global logger instance."""
    return Logger.get_instance()

