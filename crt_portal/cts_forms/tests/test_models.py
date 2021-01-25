from django.test import SimpleTestCase

from .factories import ReportFactory


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
