import logging
import os


# FIXME reusability
class Config:
    USERNAME = os.environ.get("GITLAB_USERNAME")    # FIXME
    TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")   # FIXME

    HOST_PORT = None
    KAFKA_HOST_PORT = None
    CORE_USERNAME = None
    CORE_PASSWORD = None
    VERBOSE = False
    WITH_WARNINGS = False
    BATCHER = None

    logger = logging.getLogger("base-malevich-logger")
    logger.setLevel(logging.INFO)
