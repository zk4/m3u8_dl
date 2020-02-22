#coding: utf-8
from logx import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger = logger or logging.getLogger(__name__)

    logger.info("info")
    logger.debug('debug')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

