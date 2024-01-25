import datetime
from django.test import TestCase
from utils import pdf
from unittest import mock
import pypdf
from tms.models import TMSEmail
from cts_forms.models import Report, ReportDispositionBatch, User, RetentionSchedule
from cts_forms.tests.test_data import SAMPLE_REPORT_1


class PdfTests(TestCase):
    def test_html_converts(self):
        html = "<strong>this is a test</strong>"

        converted = pdf.convert_html_to_pdf(html)

        reader = pypdf.PdfReader(converted)
        self.assertEqual(len(reader.pages), 1)
        contents = reader.pages[0].extract_text()
        self.assertEqual(contents, 'this is a test')

    def test_tms_converts(self):
        self.maxDiff = 9999999999
        report = Report(**SAMPLE_REPORT_1)
        report.public_id = 123
        email = TMSEmail(tms_id=456,
                         report=report,
                         subject='Foo subject',
                         body='Foo body',
                         html_body='<ul><li>Foo body</li></ul>',
                         recipient='Foo recipient',
                         created_at=datetime.datetime.now(),
                         completed_at=datetime.datetime.now(),
                         status=TMSEmail.SENT,
                         purpose=TMSEmail.MANUAL_EMAIL,
                         error_message='oh no bad thing')

        converted = pdf.convert_tms_to_pdf(email)

        reader = pypdf.PdfReader(converted)
        self.assertEqual(len(reader.pages), 2)
        cover = reader.pages[0].extract_text()
        contents = reader.pages[1].extract_text()
        self.assertIn('Civil Rights Division', cover)
        self.assertIn('TTY', cover)
        self.assertIn('TMS ID 456', cover)
        self.assertIn('Report ID 123', cover)
        self.assertIn('Subject Foo subject', cover)
        self.assertIn('Recipient Foo recipient', cover)
        self.assertIn('Status sent', cover)
        self.assertIn('Purpose manual', cover)
        self.assertIn('Error message oh no bad thing', cover)
        self.assertIn('Foo body', contents)

    test_user = User(username='pdf_test_user')

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='pdf_test_user').delete()
        cls.test_user.save()
        test_data = {
            **SAMPLE_REPORT_1.copy(),
            'retention_schedule': RetentionSchedule.objects.get(name='1 Year'),
            'location_name': 'batch disposition tests',
        }
        for i, schedule in enumerate(['1 Year', '3 Year', '3 Year']):
            kwargs = {
                **test_data,
                'retention_schedule': RetentionSchedule.objects.get(name=schedule)
            }
            Report.objects.create(**kwargs, public_id=f'{i}-ABC')

    @mock.patch('crequest.middleware.CrequestMiddleware.get_request',
                return_value=mock.Mock(user=test_user))
    def test_disposition_batch_converts(self, mock_get_request):
        del mock_get_request  # unused
        self.maxDiff = 9999999999

        queryset = Report.objects.filter(location_name='batch disposition tests')
        batch = ReportDispositionBatch.dispose(queryset)
        converted = pdf.convert_disposed_to_pdf(batch)

        reader = pypdf.PdfReader(converted)
        self.assertEqual(len(reader.pages), 1)
        contents = reader.pages[0].extract_text()
        self.assertIn('Civil Rights Division', contents)
        self.assertIn('Disposed Reports (1 Year) 0-ABC', contents)
        self.assertIn('Disposed Reports (3 Year) 1-ABC, 2-ABC', contents)
        self.assertIn('Disposed by pdf_test_user', contents)
        self.assertIn(f'Date of destruction {batch.disposed_date}', contents)
