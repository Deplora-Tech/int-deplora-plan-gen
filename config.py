# config.py
import logging
import sys

# Set up a logger for the whole application
logger = logging.getLogger()

formatter = logging.Formatter(
   fmt= "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers =[stream_handler, file_handler]

logger.setLevel(logging.DEBUG)