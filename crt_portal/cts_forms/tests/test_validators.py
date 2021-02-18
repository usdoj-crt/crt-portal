import io
import tempfile

from django.core.exceptions import ValidationError
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

    def setUp(self):

        self.fake_file_ok = tempfile.TemporaryFile()
        self.fake_file_ok.write(b'this is a small file')

        self.fake_file_bad = tempfile.TemporaryFile()
        self.fake_file_bad.write(b'this is big file')

    def test_file_size_uploadble(self):

        try:
            validate_file_size(self.fake_file_ok)

        except ValidationError:
            self.fail('validate_file_infection unexpectedly raised ValidationError!')


    def test_file_size_notuploadble(self):

        with self.assertRaises(ValidationError):
            validate_file_size(self.fake_file_bad)
