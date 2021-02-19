import logging
import requests
import os


from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# https://github.com/ajilaag/clamav-rest#status-codes
AV_SCAN_CODES = {
    'CLEAN': [200],
    'INFECTED': [406],
    'ERROR': [400, 412, 500, 501],
}


def _scan_file(file):
    return requests.post(settings.AV_SCAN_URL, files={'file': file}, data={'name': file.name})


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
    # Maximum file size allowed: 100 MB
    file_size = round((file.size / 1024 / 1024), 2)
    max_mb = 100

    if file_size > max_mb:
        raise ValidationError(f'This file size is: {file_size} MB this cannot be uploaded, maximum allowed: {max_mb} MB ')


def validate_content_type(file):
    # Supported content types: image/bmp, text/csv, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document,iimage/jpeg, image/gif, audio/mpeg, image/png, application/pdf, mage/tiff, text/plain, audio/wav, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

    valid_content_types = ('image/bmp', 'text/csv', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/gif', 'audio/mpeg', 'image/png', 'application/pdf', 'image/tiff', 'text/plain', 'audio/wav', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'audio/x-aiff')

    file_content_type = file.file.content_type

    if file_content_type not in valid_content_types:
        raise ValidationError(f'File content type: {file_content_type} not supported for upload, supported content types are: {valid_content_types}')


def validate_file_extension(file):

    # valid file extensions PDF, JPG, GIF, BMP, TIF, PNG, AIFF, WAV, MP3, DOC, DOCX, XLS, XLSX, CSV, TXT

    valid_file_extension = ('pdf', 'jpg', 'gif', 'bmp', 'tif', 'png', 'aiff', 'wav', 'mp3', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt')
    this_file_extension = os.path.splitext(file.name)[1][1:].lower()

    if this_file_extension not in valid_file_extension:
        raise ValidationError(f'File extension: {this_file_extension} not supported for upload, supported extensions are: {valid_file_extension}')


def validate_file_attachment(file):
    validate_file_size(file)
    validate_file_extension(file)
    validate_content_type(file)
    validate_file_infection(file)
