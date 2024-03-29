"""
Testing multilingual properties used to make messages
"""
from unittest import mock
from django.test import SimpleTestCase, TestCase
from types import SimpleNamespace

from .factories import ReportFactory

from cts_forms.models import JudicialDistrict, Report, ReportDispositionBatch, RetentionSchedule, User
from .test_data import SAMPLE_REPORT_1


class ReportSimpleTests(SimpleTestCase):

    def test_contact_full_name_with_first_and_last(self):
        report = ReportFactory.build()
        expected = f'{report.contact_first_name} {report.contact_last_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_only_first(self):
        report = ReportFactory.build(contact_last_name="")
        expected = f'{report.contact_first_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_only_last(self):
        report = ReportFactory.build(contact_first_name="")
        expected = f'{report.contact_last_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_none(self):
        report = ReportFactory.build(contact_first_name="", contact_last_name="")
        expected = ""
        self.assertEqual(report.contact_full_name, expected)

    def test_addressee_with_first_and_last(self):
        report = ReportFactory.build()
        expected = f"Dear {report.contact_full_name}"
        self.assertEqual(report.addressee, expected)

    def test_addressee_with_only_first(self):
        report = ReportFactory.build(contact_last_name="")
        expected = f"Dear {report.contact_full_name}"
        self.assertEqual(report.addressee, expected)

    def test_addressee_with_none(self):
        report = ReportFactory.build(contact_last_name="", contact_first_name="")
        expected = "Thank you for your report"
        self.assertEqual(report.addressee, expected)


class ReportTests(TestCase):
    test_user = User(username='disposition_test_user')

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user.save()
        test_data = {
            **SAMPLE_REPORT_1.copy(),
            'retention_schedule': RetentionSchedule.objects.get(name='1 Year'),
            'location_name': 'batch disposition tests',
        }
        for schedule in ['1 Year', '3 Year', '3 Year']:
            kwargs = {
                **test_data,
                'retention_schedule': RetentionSchedule.objects.get(name=schedule)
            }
            Report.objects.create(**kwargs)

    @mock.patch('crequest.middleware.CrequestMiddleware.get_request',
                return_value=mock.Mock(user=test_user))
    def test_disposition(self, mock_crequest_middleware: mock.Mock):
        reports = Report.objects.filter(location_name='batch disposition tests')
        batch = ReportDispositionBatch.dispose(reports)
        self.assertEqual(batch.disposed_by.get_username(), 'disposition_test_user')
        self.assertEqual(batch.disposed_count, 3)
        self.assertEqual(batch.disposed_reports.count(), 3)
        self.assertEqual({
            disposed.schedule.name
            for disposed in batch.disposed_reports.all()
        }, {'1 Year', '3 Year'})
        self.assertEqual({
            disposed.public_id
            for disposed in batch.disposed_reports.all()
        }, {
            original.public_id
            for original in reports.all()
        })
        self.assertTrue(all(original.disposed for original in reports))

    class DistrictEdgeCase(SimpleNamespace):
        city_user_enters: str
        expected_correction: str

    district_edge_cases = [
        DistrictEdgeCase(city_user_enters='normal city',
                         expected_correction='NORMAL CITY'),
        DistrictEdgeCase(city_user_enters='st petersburg',
                         expected_correction='SAINT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='ft petersburg',
                         expected_correction='FORT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='st. petersburg',
                         expected_correction='SAINT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='ft. petersburg',
                         expected_correction='FORT PETERSBURG'),
    ]

    def test_assign_district_edge_cases(self):
        for case in self.district_edge_cases:
            JudicialDistrict.objects.filter(city=case.expected_correction).delete()
            JudicialDistrict.objects.create(
                city=case.expected_correction, state='FL', district='123ABC')
            report = ReportFactory.build(
                location_city_town=case.city_user_enters, location_state='FL')
            district = report.assign_district()
            self.assertEqual(district, '123ABC')
