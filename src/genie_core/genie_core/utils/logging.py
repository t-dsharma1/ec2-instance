import logging
import os
from typing import ClassVar

_DEFAULT_LOGGING_LEVEL = int(os.environ.get("GENIE_LOG_LEVEL", default=logging.INFO))


class ColoredStreamHandler(logging.StreamHandler):
    """Coloured stream handler for logs."""

    cmap: ClassVar = {
        "TRACE": "[TRACE]",
        "DEBUG": "\x1b[0;36mDEBUG\x1b[0m",
        "INFO": "\x1b[0;32mINFO\x1b[0m",
        "WARNING": "\x1b[0;33mWARN\x1b[0m",
        "WARN": "\x1b[0;33mwWARN\x1b[0m",
        "ERROR": "\x1b[0;31mERROR\x1b[0m",
        "ALERT": "\x1b[0;37;41mALERT\x1b[0m",
        "CRITICAL": "\x1b[0;37;41mCRITICAL\x1b[0m",
    }

    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = self.cmap[record.levelname]
        super().emit(record)


def get_or_create_logger(
    *,
    logger_name: str = __name__,
    logging_level: int = _DEFAULT_LOGGING_LEVEL,
) -> logging.Logger:
    """Gets or creates a logger.

    Args:
        logger_name: The name of the logger.
        logging_level: The logging level of the logger.

    Returns:
        A logger.
    """
    if logger_name not in logging.Logger.manager.loggerDict.keys():
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        handler = ColoredStreamHandler()
        handler.setLevel(logging_level)
        handler.setFormatter(formatter)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)
        logger.addHandler(handler)

    else:
        logger = logging.getLogger(logger_name)

    return logger
