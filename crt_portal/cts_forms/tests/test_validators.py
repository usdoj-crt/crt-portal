import io
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase
from unittest.mock import patch

from ..validators import validate_file_infection, validate_file_size, validate_content_type, validate_file_extension


class MockHttpResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class TestInfectionValidator(TestCase):

    def setUp(self):
        self.fake_file = io.StringIO('this is a fake file')

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
            self.fail('validate_file_infection unexpectedly raised ValidationError!')

    def test_file_size_notuploadble(self):
        big_file = TemporaryUploadedFile('file.txt', b'this is a big file', 110000000, 'utf-8')

        with self.assertRaises(ValidationError):
            validate_file_size(big_file)


class TestFileContentTypeValidator(TestCase):
    def test_file_size_contenttype_ok(self):
        file = TemporaryUploadedFile('file.txt', 'text/plain', 10000, 'utf-8')
        validate_content_type(file)

    def test_file_size_contenttype_bad(self):
        file = TemporaryUploadedFile('file.zip', 'application/zip', 10000, 'utf-8')

        with self.assertRaises(ValidationError):
            validate_content_type(file)


class TestFileExtensionValidator(TestCase):
    def test_file_extension_ok(self):
        file = TemporaryUploadedFile('file.txt', '.txt', 5000, 'utf-8')
        validate_file_extension(file)

    def test_file_extension_bad(self):
        file = TemporaryUploadedFile('file.zip', '.zip', 5000, 'utf-8')

        with self.assertRaises(ValidationError):
            validate_file_extension(file)
