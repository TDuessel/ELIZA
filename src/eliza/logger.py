import os
import sys
import logging

def get_logger():
    logger = logging.getLogger("eliza_logger")
    logger.setLevel(logging.INFO)  # You can set a default level
    # Clear any default handlers if re-running in a notebook or similar environment
    logger.handlers = []
    debug_env = os.getenv("ELIZA_DEBUG", "")
    if debug_env.lower() in  ("1", "true", "yes", "on"):
        console_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(console_handler)
    else:
        null_handler = logging.NullHandler()
        logger.addHandler(null_handler)

    return logger

logger = get_logger()
