"""
Testing multilingual properties used to make messages
"""
from django.test import SimpleTestCase, TestCase
from types import SimpleNamespace

from .factories import ReportFactory

from cts_forms.models import JudicialDistrict


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
