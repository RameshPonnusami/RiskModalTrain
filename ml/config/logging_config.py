import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from .config import Config


def configure_logging(app: Flask) -> None:
    formatter = logging.Formatter(Config.LOGGING_FORMAT)

    file_handler = RotatingFileHandler(Config.LOGGING_LOCATION, maxBytes=10240, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, Config.LOGGING_LEVEL))

    app.logger.addHandler(file_handler)
