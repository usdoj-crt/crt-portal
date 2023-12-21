from django.test import TestCase
from django.apps import apps
from cts_forms.models import RetentionSchedule, Report
from cts_forms.tests.test_data import SAMPLE_REPORT_1

import importlib
migration = importlib.import_module('cts_forms.migrations.0190_backfill_ten_year_retention')


class BackfillTenYearRetentionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ten_year_schedule = RetentionSchedule.objects.get(name='10 Year')
        cls.not_ten_year_schedule = RetentionSchedule.objects.get(name='3 Year')

    def setUp(self):
        self.report = Report.objects.create(**SAMPLE_REPORT_1,
                                            retention_schedule=None,
                                            status='closed',
                                            litigation_hold=False,
                                            dj_number=None)

    def test_backfills_successfully(self):
        migration.backfill_ten_year_retention(apps, None)
        self.report.refresh_from_db()

        self.assertEqual(self.report.retention_schedule, self.ten_year_schedule)

    def test_ignores_with_dj_number(self):
        self.report.dj_number = '170-80-1234'
        self.report.save()

        migration.backfill_ten_year_retention(apps, None)
        self.report.refresh_from_db()

        self.assertIsNone(self.report.retention_schedule)

    def test_ignores_open(self):
        self.report.status = 'open'
        self.report.save()

        migration.backfill_ten_year_retention(apps, None)
        self.report.refresh_from_db()

        self.assertIsNone(self.report.retention_schedule)

    def test_ignores_litigation_hold(self):
        self.report.litigation_hold = True
        self.report.save()

        migration.backfill_ten_year_retention(apps, None)
        self.report.refresh_from_db()

        self.assertIsNone(self.report.retention_schedule)

    def test_ignores_with_retention_schedule(self):
        self.report.retention_schedule = self.not_ten_year_schedule
        self.report.save()

        migration.backfill_ten_year_retention(apps, None)
        self.report.refresh_from_db()

        self.assertEqual(self.report.retention_schedule, self.not_ten_year_schedule)
