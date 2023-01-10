import os
import time
import datetime
import logging
from yaml import safe_load as yload

# Logging levels.
LEVELS = {'FATAL': logging.FATAL,
          'ERROR': logging.ERROR,
          'WARNING': logging.WARNING,
          'INFO': logging.INFO,
          'DEBUG': logging.DEBUG}

def getConfig(filename):
    """Get Config file"""
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as fd:
            output = yload(fd.read())
    else:
        raise Exception(f'Config file {filename} does not exist.')
    return output

def getUTCnow():
    """Get UTC Time."""
    now = datetime.datetime.utcnow()
    timestamp = int(time.mktime(now.timetuple()))
    return timestamp

def checkLoggingHandler(**kwargs):
    """Check if logging handler is present and return True/False"""
    if logging.getLogger(kwargs.get('service', __name__)).hasHandlers():
        for handler in logging.getLogger(kwargs.get('service', __name__)).handlers:
            if isinstance(handler, kwargs['handler']):
                return handler
    return None

def getTimeRotLogger(**kwargs):
    """Get new Logger for logging."""
    kwargs['handler'] = logging.handlers.TimedRotatingFileHandler
    handler = checkLoggingHandler(**kwargs)
    logFile = kwargs.get('logFile', '')
    logger = logging.getLogger(kwargs.get('service', __name__))
    if not handler:
        handler = logging.handlers.TimedRotatingFileHandler(logFile,
                                                            when=kwargs.get('rotateTime', 'midnight'),
                                                            backupCount=kwargs.get('backupCount', 5))
        formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
                                      datefmt="%a, %d %b %Y %H:%M:%S")
        handler.setFormatter(formatter)
        handler.setLevel(LEVELS[kwargs.get('logLevel', 'DEBUG')])
        logger.addHandler(handler)
    logger.setLevel(LEVELS[kwargs.get('logLevel', 'DEBUG')])
    return logger