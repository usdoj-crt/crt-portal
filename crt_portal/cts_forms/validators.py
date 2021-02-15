import logging
import requests

from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def _scan_file(file):
    return requests.post(settings.AV_SCAN_URL, files={'file': file}, data={'name': file.name})


def validate_file_infection(file):
    logger.info(f'Attempting to scan file: {file}.')

    attempt = 1
    while (res := _scan_file(file)).status_code == 500:
        if (attempt := attempt + 1) > settings.AV_SCAN_MAX_ATTEMPTS:
            break

        logger.info(f'Scan attempt {attempt} failed, trying again...')
        file.seek(0)

    if settings.AV_SCAN_SUCCESS_STR not in res.text:
        raise ValidationError('The file you uploaded did not pass our security inspection, attachment failed!')

    logger.info(f'Scanning of file {file} complete.')
