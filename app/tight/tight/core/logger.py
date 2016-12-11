import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def info(*args, **kwargs):
    message = kwargs.pop('message')
    logger.info(message)