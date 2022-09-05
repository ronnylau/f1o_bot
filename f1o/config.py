import os
import sys
import logging
import configparser

logger = logging.getLogger(__name__)

# define version
VERSION = "0.1"

# Root directory of the bot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Output directory for temp files, like plot images
OUT_DIR = os.path.join(BASE_DIR, 'output')

# Where to store static data files
DATA_DIR = os.path.join(BASE_DIR, 'data')

# DEBUG
# WARNING
# ERROR
LOG_LEVEL = "DEBUG"

# Change the prefix used to call the bot
PREFIX = '!'


def create_output_dir():
    try:
        os.mkdir(OUT_DIR)
        logger.info(f"Created output directory at {OUT_DIR}.")
    except FileExistsError:
        logger.info(f"Output directory already exists at {OUT_DIR}.")


def load_config():
    try:
        if LOG_LEVEL == 'DEBUG':
            level = logging.DEBUG
        elif LOG_LEVEL == 'WARNING':
            level = logging.WARNING
        elif LOG_LEVEL == 'ERROR':
            level = logging.ERROR
        else:
            level = logging.INFO

        logging.basicConfig(
            level=level,
            format='[%(asctime)s][%(name)s] %(levelname)s: %(message)s'
        )
    except IOError:
        logger.critical(f'Could not load config.')
        sys.exit(0)


load_config()
