# logger.py
import logging
from logging.handlers import RotatingFileHandler

import sys

# Set up a logger for the whole application
logger = logging.getLogger()
sys.stdout.reconfigure(encoding="utf-8")  # Ensure stdout uses UTF-8

# Create a more detailed formatter
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

