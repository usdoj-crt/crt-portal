from cts_forms.filters import _get_date_field_from_param
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from ..filters import report_filter
from ..models import Report, ProtectedClass
from .test_data import SAMPLE_REPORT


class FilterTests(SimpleTestCase):
    def test_get_date_field_from_param(self):
        """truncate `_start` and `_end` from incoming parameters"""
        self.assertEqual(_get_date_field_from_param('create_date_start'), 'create_date')
        self.assertEqual(_get_date_field_from_param('closed_date_end'), 'closed_date')
        self.assertEqual(_get_date_field_from_param('modified_date_start'), 'modified_date')


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

        test_data['violation_summary'] = 'boat'
        Report.objects.create(**test_data)

        test_data['violation_summary'] = 'hovercraft'
        Report.objects.create(**test_data)

        # Note: Postgres websearch treats "with" as a stopword, _even in exact
        # phrase matches_, which means that word is dropped in the actual
        # query run behind the scenes.
        test_data['violation_summary'] = 'fishing boat with hovercraft'
        Report.objects.create(**test_data)

        test_data['violation_summary'] = 'fishing boat with truck'
        Report.objects.create(**test_data)

    def test_no_filters(self):
        """Returns all reports when no filters provided"""
        reports, _ = report_filter(QueryDict(''))
        self.assertEqual(reports.count(), Report.objects.count())

    def test_reported_reason(self):
        reports, _ = report_filter(QueryDict('reported_reason=age'))
        self.assertEqual(reports.count(), 2)

        reports, _ = report_filter(QueryDict('reported_reason=gender&reported_reason=language'))
        self.assertEqual(reports.count(), 1)

    def test_or_search_for_violation_summary(self):
        """
        Returns query set responsive to N terms provided as OR search
        """
        reports, _ = report_filter(QueryDict('violation_summary=plane'))
        self.assertEqual(reports.count(), 1)

        # Undocumented feature: multiple search query params in URL becomes an OR
        reports, _ = report_filter(QueryDict('violation_summary=plane&violation_summary=truck'))
        self.assertEqual(reports.count(), 3)
        for report in reports:
            self.assertEqual('plane' in report.violation_summary or 'truck' in report.violation_summary, True)

    def test_or_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20OR%20hovercraft'))
        self.assertEqual(reports.count(), 4)
        for report in reports:
            self.assertEqual('boat' in report.violation_summary or 'hovercraft' in report.violation_summary, True)

    def test_and_search(self):
        # "boat AND hovercraft" is functionally the same as "boat hovercraft"
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20hovercraft'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertIn('hovercraft', report.violation_summary)

        reports, _ = report_filter(QueryDict('violation_summary=boat%20hovercraft'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertIn('hovercraft', report.violation_summary)

    def test_or_and_search(self):
        # This query uses AND and OR without parentheses
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20hovercraft%20OR%20truck'))
        self.assertEqual(reports.count(), 3)

    def test_or_and_parens_search(self):
        # This query uses AND and OR with parentheses
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20(hovercraft%20OR%20truck)'))
        self.assertEqual(reports.count(), 2)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertEqual('hovercraft' in report.violation_summary or 'truck' in report.violation_summary, True)

    def test_not_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20-fishing'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertNotIn('fishing', report.violation_summary)

    def test_not_and_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20-fishing'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertNotIn('fishing', report.violation_summary)

    def test_not_or_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=truck%20OR%20-boat'))
        # This one is a little counter-intuitive, because one result will have "truck"
        # and "boat" in it. Why? Because the search query translates to "all entries
        # without 'boat'", and "all entries with truck, regardless of whether it has 'boat".
        self.assertEqual(reports.count(), 4)
        for report in reports:
            self.assertEqual('truck' in report.violation_summary or 'boat' not in report.violation_summary, True)

    def test_exact_phrase_search(self):
        reports, _ = report_filter(QueryDict('violation_summary="fishing boat"'))
        self.assertEqual(reports.count(), 2)
        for report in reports:
            self.assertIn('fishing boat', report.violation_summary)

    def test_exact_phrase_and_search(self):
        reports, _ = report_filter(QueryDict('violation_summary="fishing%20boat"%20AND%20hovercraft'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('fishing boat', report.violation_summary)
            self.assertIn('hovercraft', report.violation_summary)

        reports, _ = report_filter(QueryDict('violation_summary="fishing%20boat"%20hovercraft'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertIn('fishing boat', report.violation_summary)
            self.assertIn('hovercraft', report.violation_summary)

    def test_exact_phrase_or_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=hovercraft%20OR%20"fishing%20boat"'))
        self.assertEqual(reports.count(), 3)
        for report in reports:
            self.assertEqual('hovercraft' in report.violation_summary or 'fishing boat' in report.violation_summary, True)

    def test_exact_phrase_not_search(self):
        reports, _ = report_filter(QueryDict('violation_summary="fishing%20boat"%20-hovercraft'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertEqual('hovercraft' not in report.violation_summary and 'fishing boat' in report.violation_summary, True)

    def test_not_exact_phrase_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20-"fishing%20boat"'))
        self.assertEqual(reports.count(), 1)
        for report in reports:
            self.assertEqual('boat' in report.violation_summary and 'fishing boat' not in report.violation_summary, True)

    # todo: handle malformed syntax query
    def test_passthru_nested_parens_search(self):
        """
        Search queries cannot handle nested parentheses. It's a Postgres limitation.
        Still, it should gracefully handle as if there were one level of grouping.
        The result doesn't really matter for our test we just want to make sure
        it doesn't throw errors
        """
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20(hovercraft%20OR%20(truck%20AND%20fishing))'))
        self.assertEqual(reports.count(), 2)


class ReportLanguageFilterTests(TestCase):
    def setUp(self):
        test_data = SAMPLE_REPORT.copy()

        # test setup for language English
        test_data['language'] = 'en'
        Report.objects.create(**test_data)

        # test setup for language Spanish
        test_data['language'] = 'es'
        Report.objects.create(**test_data)

        # test setup for language Chinese traditional
        test_data['language'] = 'zh-hant'
        Report.objects.create(**test_data)

        # test setup for language Chinese simplified
        test_data['language'] = 'zh-hans'
        Report.objects.create(**test_data)

        # test setup for language Vietnamese
        test_data['language'] = 'vi'
        Report.objects.create(**test_data)

        # test setup for language Korean
        test_data['language'] = 'ko'
        Report.objects.create(**test_data)

        # test setup for language tagalog
        test_data['language'] = 'tl'
        Report.objects.create(**test_data)

    # report language filter test
    # report submitted in English
    def test_reported_language_en(self):
        reports, _ = report_filter(QueryDict('language=en'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Spanish
    def test_reported_language_es(self):
        reports, _ = report_filter(QueryDict('language=es'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Chinese Traditional
    def test_reported_language_hant(self):
        reports, _ = report_filter(QueryDict('language=zh-hant'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Chinese Simplified
    def test_reported_language_hans(self):
        reports, _ = report_filter(QueryDict('language=zh-hans'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Vietnamese
    def test_reported_language_vi(self):
        reports, _ = report_filter(QueryDict('language=vi'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Korean
    def test_reported_language_ko(self):
        reports, _ = report_filter(QueryDict('language=ko'))
        self.assertEqual(reports.count(), 1)

    # report submitted in Tagalog
    def test_reported_language_tl(self):
        reports, _ = report_filter(QueryDict('language=tl'))
        self.assertEqual(reports.count(), 1)
