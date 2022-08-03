from datetime import datetime
from cts_forms.forms import add_activity
from cts_forms.filters import _get_date_field_from_param
from django.contrib.auth.models import User
from actstream import registry
from actstream.models import actor_stream
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase, TransactionTestCase
import pytz

from ..filters import report_filter
from api.filters import form_letters_filter, autoresponses_filter
from ..models import Report, ProtectedClass, FormLettersSent
from .test_data import SAMPLE_REPORT_1, SAMPLE_REPORT_2, SAMPLE_REPORT_3, SAMPLE_REPORT_4


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
        language = ProtectedClass.objects.get(value='language')
        test_data = SAMPLE_REPORT_1.copy()

        test_data['violation_summary'] = 'plane'
        r1 = Report.objects.create(**test_data)
        r1.protected_class.add(age)

        test_data['violation_summary'] = 'truck'
        r2 = Report.objects.create(**test_data)
        r2.protected_class.add(age)
        r2.protected_class.add(gender)
        r2.protected_class.add(language)

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

        test_data['violation_summary'] = 'boat plane'
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

    def test_contact_phone(self):
        test_data2 = SAMPLE_REPORT_2.copy()
        Report.objects.create(**test_data2)
        test_data3 = SAMPLE_REPORT_3.copy()
        Report.objects.create(**test_data3)
        reports, _ = report_filter(QueryDict('contact_phone=555'))
        self.assertEqual(reports.count(), 2)
        reports, _ = report_filter(QueryDict('contact_phone=202-555-5555'))
        self.assertEqual(reports.count(), 1)
        # Should ignore any non numberical characters and search against blocks
        reports, _ = report_filter(QueryDict('contact_phone=(202)%20555.5555'))
        self.assertEqual(reports.count(), 1)
        # Since non numeric characters are stripped, it should return all results.
        reports, _ = report_filter(QueryDict('contact_phone=Hello'))
        self.assertEqual(reports.count(), 9)

    def test_or_search_for_violation_summary(self):
        """
        Returns query set responsive to N terms provided as OR search
        """
        reports, _ = report_filter(QueryDict('violation_summary=plane'))
        self.assertEqual(reports.count(), 2)

    def test_or_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20OR%20hovercraft'))
        self.assertEqual(reports.count(), 5)
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

        # multiple OR
        reports, _ = report_filter(QueryDict('violation_summary=boat%20(hovercraft%20OR%20truck%20OR%20plane)'))
        self.assertEqual(reports.count(), 3)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertEqual('hovercraft' in report.violation_summary or 'truck' in report.violation_summary or 'plane' in report.violation_summary, True)

    def test_not_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20-fishing'))
        self.assertEqual(reports.count(), 2)
        for report in reports:
            self.assertIn('boat', report.violation_summary)
            self.assertNotIn('fishing', report.violation_summary)

    def test_not_and_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20-fishing'))
        self.assertEqual(reports.count(), 2)
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

    def test_not_parens_search(self):
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20-(fishing%20AND%20hovercraft)'))
        # Also may be counter-intuitive, because we want results that lack BOTH "fishing"
        # and "hovercraft", so "fishing boat with hovercraft" is removed, but "fishing boat
        # with truck" is allowed
        self.assertEqual(reports.count(), 3)

        # Should also assume AND
        reports, _ = report_filter(QueryDict('violation_summary=boat%20-(fishing%20AND%20hovercraft)'))
        self.assertEqual(reports.count(), 3)

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
        self.assertEqual(reports.count(), 2)
        for report in reports:
            self.assertEqual('boat' in report.violation_summary and 'fishing boat' not in report.violation_summary, True)

    def test_passthru_nested_parens_search(self):
        """
        Search queries cannot handle nested parentheses. It's a Postgres limitation.
        Still, it should gracefully handle as if there were one level of grouping.
        The result doesn't really matter for our test we just want to make sure
        it doesn't throw errors
        """
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20(hovercraft%20OR%20(truck%20AND%20fishing))'))
        self.assertEqual(reports.count(), 2)


# This is a separate test suite from the above search query tests because
# test suites don't like it when databases throw errors inside of them
class ReportFilterErrorTests(TransactionTestCase):
    @classmethod
    def setUpTestData(self):
        test_data = SAMPLE_REPORT_1.copy()

        test_data['violation_summary'] = 'plane'
        self.report1 = Report.objects.create(**test_data)

        test_data['violation_summary'] = 'truck'
        self.report2 = Report.objects.create(**test_data)

    def test_malformed_parens_search(self):
        """
        If parens has a syntax error, don't throw errors. Do our best with the query,
        returning an empty query set if necessary.
        """
        reports, _ = report_filter(QueryDict('violation_summary=boat%20AND%20(hovercraft%20OR%20truck))'))
        self.assertEqual(reports.count(), 0)


class ReportLanguageFilterTests(TestCase):
    @classmethod
    def setUpTestData(self):
        test_data = SAMPLE_REPORT_1.copy()

        # test setup for language English
        test_data['language'] = 'en'
        self.report1 = Report.objects.create(**test_data)

        # test setup for language Spanish
        test_data['language'] = 'es'
        self.report2 = Report.objects.create(**test_data)

        # test setup for language Chinese traditional
        test_data['language'] = 'zh-hant'
        self.report3 = Report.objects.create(**test_data)

        # test setup for language Chinese simplified
        test_data['language'] = 'zh-hans'
        self.report4 = Report.objects.create(**test_data)

        # test setup for language Vietnamese
        test_data['language'] = 'vi'
        self.report5 = Report.objects.create(**test_data)

        # test setup for language Korean
        test_data['language'] = 'ko'
        self.report6 = Report.objects.create(**test_data)

        # test setup for language tagalog
        test_data['language'] = 'tl'
        self.report7 = Report.objects.create(**test_data)

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


class FormLettersFilterTests(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.report1 = Report.objects.create(**SAMPLE_REPORT_1)
        self.report2 = Report.objects.create(**SAMPLE_REPORT_2)
        self.report3 = Report.objects.create(**SAMPLE_REPORT_3)
        self.report4 = Report.objects.create(**SAMPLE_REPORT_4)
        registry.register(User)
        add_activity(self.user, "Contacted complainant:", "Email sent: 'EOS - Department of Ed OCR Referral Form Letter' to cookiemonster@fakeemail.com via govDelivery TMS", self.report4)
        first_action = actor_stream(self.user).first()
        first_action.timestamp = datetime(2022, 4, 12, 14, 56, 53, tzinfo=pytz.utc)
        first_action.save()
        add_activity(self.user, "Contacted complainant:", "Email sent: 'EOS - EEOC Referral Form Letter' to    eileenmcfarland@navapbc.com via govDelivery TMS", self.report2)
        second_action = actor_stream(self.user).first()
        second_action.timestamp = datetime(2022, 4, 12, 17, 30, 53, tzinfo=pytz.utc)
        second_action.save()
        add_activity(self.user, "Contacted complainant:", "Email sent: 'EOS - EEOC Referral Form Letter' to  bigbird@fake.com via govDelivery TMS", self.report3)
        third_action = actor_stream(self.user).first()
        third_action.timestamp = datetime(2022, 4, 15, 10, 56, 53, tzinfo=pytz.utc)
        third_action.save()
        add_activity(self.user, "Added comment: ", "Email sent: 'SPL - Standard Form Letter' to gregory94@example.com via govDelivery TMS", self.report4)
        fourth_action = actor_stream(self.user).first()
        fourth_action.timestamp = datetime(2022, 5, 1, 10, 56, 53, tzinfo=pytz.utc)
        fourth_action.save()
        add_activity(self.user, "Contacted complainant:", "Email sent: 'CRT - Request for Agency Review' to hernandezcolleen@example.com via govDelivery TMS", self.report1)
        fifth_action = actor_stream(self.user).first()
        fifth_action.timestamp = datetime(2022, 5, 4, 10, 56, 53, tzinfo=pytz.utc)
        fifth_action.save()
        FormLettersSent.refresh_view()

    def test_date_filter(self):
        request_one_day = QueryDict(mutable=True)
        request_one_day.update({
            "assigned_section": "CRM",
            "start_date": "2022-04-12",
            "end_date": "2022-04-12"})
        request_multi_day = QueryDict(mutable=True)
        request_multi_day.update({
            "assigned_section": "CRM",
            "start_date": "2022-04-12",
            "end_date": "2022-04-15"})
        result_one_day = form_letters_filter(request_one_day)
        result_multi_day = form_letters_filter(request_multi_day)
        self.assertEqual(result_one_day["total_form_letters"], 2)
        self.assertEqual(result_multi_day["total_form_letters"], 3)

    def test_date_filter_no_results(self):
        request = QueryDict(mutable=True)
        request.update({"assigned_section": "ADM",
                        "start_date": "2022-04-1",
                        "end_date": "2022-04-11"})
        result = form_letters_filter(request)
        self.assertEqual(result["total_form_letters"], 0)

    def test_section_filter_no_results(self):
        request = QueryDict(mutable=True)
        request.update({"assigned_section": "FCS"})
        result = form_letters_filter(request)
        self.assertEqual(result["total_form_letters"], 0)

    def test_section_filter_one_result(self):
        request = QueryDict(mutable=True)
        request.update({"assigned_section": "ADM"})
        result = form_letters_filter(request)
        self.assertEqual(result["total_form_letters"], 1)

    def test_section_filter_and_date_filter(self):
        request = QueryDict(mutable=True)
        request.update({"assigned_section": "CRM", "start_date": "2022-04-11", "end_date": "2022-04-14"})
        result = form_letters_filter(request)
        self.assertEqual(result["total_form_letters"], 2)


class AutoResponsesFilterTests(TestCase):
    @classmethod
    def setUpTestData(self):
        report_1 = Report.objects.create(**SAMPLE_REPORT_1)
        report_1.create_date = datetime(2022, 4, 12, 18, 17, 52, 0, tzinfo=pytz.utc)
        report_1.save()
        report_2 = Report.objects.create(**SAMPLE_REPORT_2)
        report_2.create_date = datetime(2022, 4, 13, 18, 17, 52, 0, tzinfo=pytz.utc)
        report_2.save()
        report_3 = Report.objects.create(**SAMPLE_REPORT_3)
        report_3.create_date = datetime(2022, 2, 1, 18, 17, 52, 0, tzinfo=pytz.utc)
        report_3.save()
        report_4 = Report.objects.create(**SAMPLE_REPORT_4)
        report_4.create_date = datetime(2022, 2, 4, 18, 17, 52, 0, tzinfo=pytz.utc)
        report_4.save()

    def test_no_section_filter(self):
        request = QueryDict(mutable=True)
        request.update({"start_date": "2022-04-12", "end_date": "2022-04-13"})
        total_autoresponses = autoresponses_filter(request)
        self.assertEqual(total_autoresponses, 0)

    def test_only_section_filter(self):
        request = QueryDict(mutable=True)
        request.update({"assigned_section": "CRM"})
        total_autoresponses = autoresponses_filter(request)
        self.assertEqual(total_autoresponses, 3)

    def test_date_and_section_filter(self):
        request = QueryDict(mutable=True)
        request.update({"start_date": "2022-02-01", "end_date": "2022-02-13", "assigned_section": "CRM"})
        total_autoresponses = autoresponses_filter(request)
        self.assertEqual(total_autoresponses, 2)
