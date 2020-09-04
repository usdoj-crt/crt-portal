from cts_forms.filters import _get_date_field_from_param
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from ..filters import report_filter
from ..models import Report
from .test_data import SAMPLE_REPORT


class FilterTests(SimpleTestCase):
    def test_get_date_field_from_param(self):
        """truncate `_start` and `_end` from incoming parameters"""
        self.assertEquals(_get_date_field_from_param('create_date_start'), 'create_date')
        self.assertEquals(_get_date_field_from_param('closed_date_end'), 'closed_date')
        self.assertEquals(_get_date_field_from_param('modified_date_start'), 'modified_date')


class ReportFilterTests(TestCase):
    def setUp(self):
        test_data = SAMPLE_REPORT.copy()
        test_data['violation_summary'] = 'plane'
        Report.objects.create(**test_data)
        test_data['violation_summary'] = 'truck'
        Report.objects.create(**test_data)

    def test_no_filters(self):
        """Returns all reports when no filters provided"""
        reports, _ = report_filter(QueryDict(''))
        self.assertEquals(reports.count(), Report.objects.count())

    def test_or_search_for_violation_summary(self):
        """
        Returns queryset responsive to N terms provided as OR search
        """
        reports, _ = report_filter(QueryDict('violation_summary=plane'))
        self.assertEquals(reports.count(), 1)

        reports, _ = report_filter(QueryDict('violation_summary=plane&violation_summary=truck'))
        self.assertEquals(reports.count(), 2)
