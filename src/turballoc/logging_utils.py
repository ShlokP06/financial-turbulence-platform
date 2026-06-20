import logging
from turballoc.config import settings

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

def get_logger(name):
    return logging.getLogger(name)
