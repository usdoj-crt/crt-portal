from cts_forms.filters import _get_date_field_from_param
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from ..filters import report_filter
from ..models import Report, ProtectedClass
from .test_data import SAMPLE_REPORT


class FilterTests(SimpleTestCase):
    def test_get_date_field_from_param(self):
        """truncate `_start` and `_end` from incoming parameters"""
        self.assertEquals(_get_date_field_from_param('create_date_start'), 'create_date')
        self.assertEquals(_get_date_field_from_param('closed_date_end'), 'closed_date')
        self.assertEquals(_get_date_field_from_param('modified_date_start'), 'modified_date')


class ReportFilterTests(TestCase):
    def setUp(self):
        age = ProtectedClass.objects.get(value='age')
        gender = ProtectedClass.objects.get(value='gender')
        test_data = SAMPLE_REPORT.copy()
        test_data['violation_summary'] = 'plane'
        r1 = Report.objects.create(**test_data)
        r1.protected_class.add(age)
        test_data['violation_summary'] = 'truck'
        r2 = Report.objects.create(**test_data)
        r2.protected_class.add(age)
        r2.protected_class.add(gender)

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

    def test_reported_reason(self):
        reports, _ = report_filter(QueryDict('reported_reason=age'))
        self.assertEquals(reports.count(), 2)

        reports, _ = report_filter(QueryDict('reported_reason=gender&reported_reason=language'))
        self.assertEquals(reports.count(), 1)
