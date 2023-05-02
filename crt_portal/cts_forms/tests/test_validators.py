"""
Testing email validation
"""
import requests

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase
from unittest.mock import patch

from ..attachments import (
    ALLOWED_CONTENT_TYPES,
)
from ..validators import (
    validate_content_type,
    validate_dj_number,
    validate_email_address,
    validate_file_extension,
    validate_file_infection,
    validate_file_size,
    validate_filename,
)


class MockHttpResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class TestInfectionValidator(TestCase):

    def setUp(self):
        self.fake_file = TemporaryUploadedFile('file.txt', 'text/plain', 10000, 'utf-8')

    @patch('requests.post')
    def test_av_service_unavailable(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError('service unavailable')

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch('cts_forms.validators._scan_file')
    def test_validation_fails_on_av_service_error(self, mock_scan_file):
        mock_scan_file.return_value = MockHttpResponse(500, 'error text')

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch('cts_forms.validators._scan_file')
    def test_validation_fails_on_non_success_response(self, mock_scan_file):
        mock_scan_file.return_value = MockHttpResponse(406, 'infected!')

        with self.assertRaises(ValidationError):
            validate_file_infection(self.fake_file)

    @patch('cts_forms.validators._scan_file')
    def test_validation_succeeds_on_success_response(self, mock_scan_file):
        mock_scan_file.return_value = MockHttpResponse(200, 'clean!')

        try:
            validate_file_infection(self.fake_file)
        except ValidationError:
            self.fail('validate_file_infection unexpectedly raised ValidationError!')


class TestFileSizeValidator(TestCase):

    def test_file_size_uploadble(self):
        small_file = TemporaryUploadedFile('file.txt', b'this is a small file', 10000, 'utf-8')

        try:
            validate_file_size(small_file)

        except ValidationError:
            self.fail('validate_file_size unexpectedly raised ValidationError!')

    def test_file_size_notuploadble(self):
        big_file = TemporaryUploadedFile('file.txt', b'this is a big file', 110000000, 'utf-8')

        with self.assertRaises(ValidationError):
            validate_file_size(big_file)


class TestFileNameValidator(TestCase):

    def test_file_name_valid(self):
        valid_filename = TemporaryUploadedFile('file-name_acceptable 03152021.txt', b'This filename is supported', 5000, 'utf-8')

        try:
            validate_filename(valid_filename)

        except ValidationError:
            self.fail('validate_file_size unexpectedly raised ValidationError!')

    def test_all_special_characters(self):

        for letter in "@!#$%^()&*<>?|}{~:,;'][\\\"":

            invalid_filename = TemporaryUploadedFile(
                f'FileName.has.special.character.{letter}.txt',
                b'Special character not supported for filename ',
                5000,
                'utf-8',
            )

            with self.assertRaises(ValidationError):
                validate_filename(invalid_filename)


class TestDjNumberValidator(TestCase):

    def test_validate_dj_number_valid(self):
        validate_dj_number('170-80-1234')

    def test_validate_dj_number_valid_extra_dash(self):
        validate_dj_number('170-USE-80-1234')

    def test_validate_dj_number_statute(self):
        with self.assertRaisesRegex(ValidationError, r'statute number 666 is invalid'):
            validate_dj_number('666-26S-1234')

    def test_validate_dj_number_district(self):
        with self.assertRaisesRegex(ValidationError, r'district number 666 is invalid'):
            validate_dj_number('170-666-1234')

    def test_validate_dj_number_sequence_digits(self):
        with self.assertRaisesRegex(ValidationError, r'sequence number 12a4 must'):
            validate_dj_number('170-26S-12a4')

    def test_validate_dj_number_sequence_missing(self):
        with self.assertRaisesRegex(ValidationError, r'sequence number  must'):
            validate_dj_number('170-26S-')

    def test_validate_dj_number_sequence_too_large(self):
        with self.assertRaisesRegex(ValidationError, r'sequence number 12345 must'):
            validate_dj_number('170-26S-12345')


# use this to match the class signature expected in validate_content_type, file.file.content_type
class FileWrapper:
    def __init__(self, file):
        self.file = file


class TestFileContentTypeValidator(TestCase):
    def test_file_size_contenttype_ok(self):
        for content_type in ALLOWED_CONTENT_TYPES:
            file = FileWrapper(TemporaryUploadedFile('file', content_type, 10000, 'utf-8'))
            validate_content_type(file)

    def test_file_size_contenttype_bad(self):
        some_bad_content_types = [
            'application/gzip',
            'application/vnd.rar',
            'application/x-7z-compressed',
            'application/x-httpd-php',
            'application/x-sh',
            'application/x-tar',
            'application/zip',
            'text/javascript',
        ]
        for content_type in some_bad_content_types:
            file = FileWrapper(TemporaryUploadedFile('file', content_type, 10000, 'utf-8'))

            with self.assertRaises(ValidationError):
                validate_content_type(file)


class TestFileExtensionValidator(TestCase):
    def test_file_extension_ok(self):
        file = TemporaryUploadedFile('file.txt', 'text/plain', 5000, 'utf-8')

        try:
            validate_file_extension(file)

        except ValidationError:
            self.fail('validate_file_extension unexpectedly raised ValidationError!')

    def test_file_extension_bad(self):
        file = TemporaryUploadedFile('file.zip', 'application/zip', 5000, 'utf-8')

        with self.assertRaises(ValidationError):
            validate_file_extension(file)


class TestEmailValidator(TestCase):
    def test_valid_email_ok(self):
        try:
            validate_email_address('name@domain.com')
        except ValidationError:
            self.fail('test_valid_email_ok unexpectedly raised ValidationError!')

    def test_invalid_email_raises(self):
        with self.assertRaises(ValidationError):
            validate_email_address('thisisnotanemailaddress')

    def test_chinese_email_ok(self):
        try:
            validate_email_address('用户@例子.广告')
        except ValidationError:
            self.fail('validate_email_address unexpectedly raised ValidationError')

    def test_hindi_email_ok(self):
        try:
            validate_email_address('अजय@डाटा.भारत')
        except ValidationError:
            self.fail('test_hindi_email_ok unexpectedly raised ValidationError')

    def test_ukrainian_email_ok(self):
        try:
            validate_email_address('квіточка@пошта.укр')
        except ValidationError:
            self.fail('test_ukrainian_email_ok unexpectedly raised ValidationError')

    def test_greek_email_ok(self):
        try:
            validate_email_address('χρήστης@παράδειγμα.ελ')
        except ValidationError:
            self.fail('test_greek_email_ok unexpectedly raised ValidationError')

    def test_german_email_ok(self):
        try:
            validate_email_address('Dörte@Sörensen.example.com')
        except ValidationError:
            self.fail('test_german_email_ok unexpectedly raised ValidationError')

    def test_russian_email_ok(self):
        try:
            validate_email_address('коля@пример.рф')
        except ValidationError:
            self.fail('test_russian_email_ok unexpectedly raised ValidationError')
