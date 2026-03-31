import logging
import os

_logger: logging.Logger | None = None


def _create_logger() -> logging.Logger:
    log = logging.getLogger("edh_utils")
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log.setLevel(getattr(logging, level, logging.INFO))
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(funcName)s @ %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    ))
    log.addHandler(handler)
    return log


def logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = _create_logger()
    return _logger
