import logging
import logging.handlers
import traceback
import sys
import os

DEFAULT_LOGGER_NAME = os.getenv('LOGGER_NAME', 'DataEng')


def init_logging(logger_name=DEFAULT_LOGGER_NAME,
                 log_level=logging.DEBUG,
                 stream=None,
                 file_handler=False):
    # logging
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    if stream is None:
        stream = sys.stderr
    ch = logging.StreamHandler(stream=stream)
    ch.setLevel(log_level)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    if file_handler:
        fh = logging.FileHandler(f'./logs/{DEFAULT_LOGGER_NAME}.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def test_exception_logging():
    raise Exception('Exception from log_utils.py!')


def get_default_logger():
    return logging.getLogger(DEFAULT_LOGGER_NAME)


def exception_message_with_stack_trace(ex):
    return ''.join(reversed(traceback.format_exception(etype=type(ex), value=ex,
                                                       tb=ex.__traceback__)))