# logger.py
import logging
from logging.handlers import RotatingFileHandler

import sys

# Set up a logger for the whole application
logger = logging.getLogger()

formatter = logging.Formatter(
   fmt= "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=3
) 

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers =[stream_handler, file_handler]

logger.setLevel(logging.DEBUG)