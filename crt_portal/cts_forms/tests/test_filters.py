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

        # http://0.0.0.0:8000/form/view/?status=new&status=open&no_status=false&language=es&language=en&language=zh-hant&language=zh-hans&language=vi&language=ko&language=tl

        # test setup for language English
        r3 = Report.objects.create(**test_data)
        r3.protected_class.add(age)
        r3.protected_class.add(gender)
        test_data['language'] = 'en'

        # test setup for language Spanish
        r4 = Report.objects.create(**test_data)
        r4.protected_class.add(age)
        r4.protected_class.add(gender)
        test_data['language'] = 'es'

        # test setup for language Chinese traditional
        r5 = Report.objects.create(**test_data)
        r5.protected_class.add(age)
        r5.protected_class.add(gender)
        test_data['language'] = 'zh-hant'

        # test setup for language Chinese simplified
        r6 = Report.objects.create(**test_data)
        r6.protected_class.add(age)
        r6.protected_class.add(gender)
        test_data['language'] = 'zh-hans'

        # test setup for language Vietnamese
        r7 = Report.objects.create(**test_data)
        r7.protected_class.add(age)
        r7.protected_class.add(gender)
        test_data['language'] = 'vi'

        # test setup for language Korean
        r8 = Report.objects.create(**test_data)
        r8.protected_class.add(age)
        r8.protected_class.add(gender)
        test_data['language'] = 'ko'

        # test setup for language tagalog
        r9 = Report.objects.create(**test_data)
        r9.protected_class.add(age)
        r9.protected_class.add(gender)
        test_data['language'] = 'tl'

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
        self.assertEquals(reports.count(), 9)

    def test_reported_reason(self):
        reports, _ = report_filter(QueryDict('reported_reason=age'))
        self.assertEquals(reports.count(), 9)

        reports, _ = report_filter(QueryDict('reported_reason=gender&reported_reason=language'))
        self.assertEquals(reports.count(), 8)

    # language=es&language=en&language=zh-hant&language=zh-hans&language=vi&language=ko&language=tl
    # report language filter test
    def test_reported_language_en(self):
        reports, _ = report_filter(QueryDict('language=en'))
        self.assertEquals(reports.count(), 4)

    def test_reported_language_es(self):
        reports, _ = report_filter(QueryDict('language=es'))
        self.assertEquals(reports.count(), 1)

    def test_reported_language_hant(self):
        reports, _ = report_filter(QueryDict('language=zh-hant'))
        self.assertEquals(reports.count(), 1)

    def test_reported_language_hans(self):
        reports, _ = report_filter(QueryDict('language=zh-hans'))
        self.assertEquals(reports.count(), 1)

    def test_reported_language_vi(self):
        reports, _ = report_filter(QueryDict('language=vi'))
        self.assertEquals(reports.count(), 1)

    def test_reported_language_ko(self):
        reports, _ = report_filter(QueryDict('language=ko'))
        self.assertEquals(reports.count(), 1)

    def test_reported_language_tl(self):
        reports, _ = report_filter(QueryDict('language=tl'))
        self.assertEquals(reports.count(), 1)
