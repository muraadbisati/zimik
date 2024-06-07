import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__) #Instantiates getlogger class from logging module,object logger gets the name of and inherits the properties of log.py
logger.setLevel(logging.INFO)# sets the logging level for the logger to(INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')#Instantiates Formatter class from logging module,object defines the format of the log messages.(time,logging level,message)

# Define the maximum size for the log file (in bytes)
max_log_size = 10 * 1024  # 10 KB

# Create a RotatingFileHandler with log rotation settings
file_handler = RotatingFileHandler('logs/app.log', maxBytes=max_log_size, backupCount=2)#The RotatingFileHandler is one type of handler(implemented as class) provided by the logging.handlers submodule  handle log files and supports log rotation based on criteria
file_handler.setFormatter(formatter)#By passing the formatter variable, we ensure that the log messages written to the log file, are formatted according to the structure defined using logging.formatter class above
logger.addHandler(file_handler)#assigning handler  to the logger object


def log_error(error_message):
    logger.error(error_message)
    with open("logs/app.log", "a") as log_file:
        log_file.write(f"Error: {error_message}\n")

