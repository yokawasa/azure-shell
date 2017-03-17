import os
import logging

_DEFAULT_AZURE_SHELL_LOG_LEVEL = 'INFO'
_DEFAULT_AZURE_SHELL_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'

def init_logger(name, log_file,
                log_level = _DEFAULT_AZURE_SHELL_LOG_LEVEL,
                log_format = _DEFAULT_AZURE_SHELL_LOG_FORMAT):

    logger = logging.getLogger(name)
    handler = logging.FileHandler(os.path.expanduser(log_file))
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    switcher = {
        'CRITICAL': logging.CRITICAL,
        'ERROR':    logging.ERROR,
        'WARNING':  logging.WARNING,
        'INFO':     logging.INFO,
        'DEBUG':    logging.DEBUG
    }
    logger.setLevel(switcher.get(log_level.upper(),logging.INFO))
