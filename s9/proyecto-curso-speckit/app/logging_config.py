"""Logging configuration.

Per Artículo IV.5 (Security):
- Errors logged internally with full details (stack traces, exception messages)
- BUT NEVER exposed to client (client always gets generic 500 response)
- Passwords NEVER logged in any form
"""

import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "error.log",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "app": {
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


def configure_logging():
    """Apply logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    configure_logging()
    return logging.getLogger(name)
