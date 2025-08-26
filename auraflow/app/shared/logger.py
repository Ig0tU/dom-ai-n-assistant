import logging
import sys

def setup_logger():
    """Sets up the main logger for the application."""
    logger = logging.getLogger("AuraFlow")
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

log = setup_logger()
