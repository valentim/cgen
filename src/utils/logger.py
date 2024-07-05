import logging
from config.settings import Settings


def get_logger(module_name: str):
    logging.basicConfig(
        level=Settings().LOGGING_LEVEL,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(module_name)
