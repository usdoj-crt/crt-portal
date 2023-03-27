
"""
Validating file uploads
Uploads are only available for CRT staff. Uploads are vetted with ClamAV.
"""
import logging
import requests
import os
import re
from email_validator import validate_email, EmailNotValidError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .attachments import MAX_FILE_SIZE_MB, ALLOWED_CONTENT_TYPES, ALLOWED_FILE_EXTENSIONS

logger = logging.getLogger(__name__)

# https://github.com/ajilaag/clamav-rest#status-codes
AV_SCAN_CODES = {
    'CLEAN': [200],
    'INFECTED': [406],
    'ERROR': [400, 412, 500, 501],
}


def validate_filename(file):
    # special character not accepted
    # for file name
    thisfile = file.name

    special_characters = r"[@!#$%^()&*<>?/\|}{~:,;\"\'\]\[\\]"

    # regex_match = re.compile({special_characters})
    regex_match = re.search(special_characters, thisfile)

    # verify if the regex search math found any special character.
    if regex_match is not None:

        raise ValidationError(f'Filename: {thisfile} have special characters, rename file before upload. Acceptable file name special characters are - (dash) and _ (underscore).')


def _scan_file(file):
    try:
        return requests.post(settings.AV_SCAN_URL, files={'file': file}, data={'name': file.name}, timeout=25)
    except requests.exceptions.ConnectionError:
        raise ValidationError('We were unable to complete a security inspection of the file, please try again or contact support for assistance.')


def validate_file_infection(file):
    logger.info(f'Attempting to scan file: {file}.')

    attempt = 1

    # on large(ish) files (>10mb), the clamav-rest API sometimes times out
    # on the first couple of attempts. We retry the scan up to our maximum
    # in these cases
    while (res := _scan_file(file)).status_code in AV_SCAN_CODES['ERROR']:
        if (attempt := attempt + 1) > settings.AV_SCAN_MAX_ATTEMPTS:
            break

        logger.info(f'Scan attempt {attempt} failed, trying again...')
        file.seek(0)

    if res.status_code not in AV_SCAN_CODES['CLEAN']:
        logger.info(f'Scan of {file} revealed potential infection - rejecting!')
        raise ValidationError('The file you uploaded did not pass our security inspection, attachment failed!')

    logger.info(f'Scanning of file {file} complete.')


def validate_file_size(file):
    file_size = round((file.size / 1024 / 1024), 2)

    if file_size > MAX_FILE_SIZE_MB:
        raise ValidationError(f'This file size is: {file_size} MB this cannot be uploaded, maximum allowed: {MAX_FILE_SIZE_MB} MB ')


def validate_content_type(file):
    file_content_type = file.file.content_type

    if file_content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(f'File content type: {file_content_type} not supported for upload, supported content types are: {ALLOWED_CONTENT_TYPES}')


def validate_file_extension(file):
    this_file_extension = os.path.splitext(file.name)[1].lower()

    if this_file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(f'File extension: {this_file_extension} not supported for upload, supported extensions are: {ALLOWED_FILE_EXTENSIONS}')


def validate_file_attachment(file):
    validate_filename(file)
    validate_file_size(file)
    validate_file_extension(file)
    validate_content_type(file)
    validate_file_infection(file)


def validate_email_address(email):
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise ValidationError(_('Enter a valid email address.'))
