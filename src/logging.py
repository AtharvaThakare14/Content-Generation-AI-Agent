# Import necessary libraries
import os
import logging
from datetime import datetime
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

logs_path = os.path.join(os.getcwd(), "tmp/", LOG_FILE)

os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configure the logging module
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.DEBUG,
    format='[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s: %(message)s'
    # Define the log message format. Here:
    # - %(asctime)s: The timestamp of the log message
    # - %(lineno)d: The line number where the log message was issued
    # - %(name)s: The name of the logger (usually the name of the Python module)
    # - %(levelname)s: The log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    # - %(message)s: The actual log message content
)
