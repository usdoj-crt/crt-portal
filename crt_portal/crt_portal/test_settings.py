import logging

from .settings import *  # noqa: F401,F403

logger = logging.getLogger(__name__)

lock_file_name = os.path.join(BASE_DIR, 'NO_ZIP.txt')  # noqa: F405

with open(lock_file_name, 'w') as f:
    logger.info('Loading test settings')
