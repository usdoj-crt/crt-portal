import logging

from .settings import *  # noqa: F401,F403

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lock_file_name = os.path.join(BASE_DIR, 'NO_ZIP.txt')

with open(lock_file_name, 'w') as f:
    logger.info('Loading test settings')
