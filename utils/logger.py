# utils/logger.py
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger_format = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s"
    )
    return logging.getLogger(name)
