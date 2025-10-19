from app.config.settings import ENVIRONMENT
from app.constants.enum import Environment


def is_dev() -> bool:
    return ENVIRONMENT == Environment.DEVELOPMENT


def is_prod() -> bool:
    return ENVIRONMENT == Environment.PRODUCTION