"""
Internal views and misc views
"""
import copy
import io
import json
import secrets
from datetime import date, timedelta
import pypdf
import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from unittest.mock import patch

from testfixtures import LogCapture

from ..forms import ComplaintOutreach, ContactEditForm, ReportEditForm, add_activity
from ..model_variables import PRIMARY_COMPLAINT_CHOICES
from ..models import Profile, Report, ReportAttachment, ProtectedClass, PROTECTED_MODEL_CHOICES, CommentAndSummary, Campaign, BannerMessage, RetentionSchedule, SavedSearch, NotificationPreference, Resource, Tag
from .test_data import SAMPLE_REPORT_1, SAMPLE_REPORT_3, SAMPLE_REPORT_4
from .factories import ReportFactory
from .utils import assertSoupFinds, assertSoupSelects


class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        sample_profile = {
            'intake_filters': 'ADM',
            'user_id': self.user.id
        }
        self.test_profile = Profile.objects.create(**sample_profile)
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.form_data = {'type': 'profile_form'}
        self.url = reverse('crt_forms:cts-forms-profile')

    def tearDown(self):
        self.user.delete()

    def test_profile_form_save(self):
        """Profile create on successful POST"""
        new_intake_filters = ['VOT', 'ADM']
        self.form_data.update({'intake_filters': new_intake_filters})
        self.client.post(self.url, self.form_data, follow=True)
        self.test_profile.refresh_from_db()
        self.assertEqual(self.test_profile.intake_filters, 'VOT,ADM')


class OutreachTests(TestCase):

    def setUp(self):
        self.campaign = Campaign.objects.create(internal_name="Fake Campaign")
        self.other_campaign = Campaign.objects.create(internal_name="Other Campaign")
        self.test_report = Report.objects.create(
            **SAMPLE_REPORT_1,
            origination_utm_campaign=self.campaign)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.form_data = {'type': ComplaintOutreach.CONTEXT_KEY}

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id})

    def tearDown(self):
        self.user.delete()

    def test_update_campaign(self):
        new_campaign = self.other_campaign
        self.form_data.update({'origination_utm_campaign': self.other_campaign.uuid})
        response = self.client.post(self.url, self.form_data, follow=True)
        self.assertEqual(response.context['data'].origination_utm_campaign, new_campaign)

        self.test_report.refresh_from_db()
        self.assertEqual(self.test_report.origination_utm_campaign, new_campaign)


class NotificationManagementTests(TestCase):
    def setUp(self):
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user('DELETE_USER', 'test@usdoj.gov', '')
        self.url = '/form/notifications/'
        self.client = Client()
        self.client.login(username='DELETE_USER', password='')  # nosec
        NotificationPreference.objects.all().delete()
        self.preference = NotificationPreference.objects.get_or_create(user=self.user)[0]
        self.preference.assigned_to = 'individual'
        self.preference.save()

    def test_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assertSoupFinds(response, 'h2', string='Notification Management')
        assertSoupFinds(response, 'button', string='Save preferences')

    def test_includes_complaint_assignment_settings(self):
        response = self.client.get(self.url)
        assertSoupFinds(response, 'label', string=re.compile('.*Complaint assignments.*'))
        assertSoupSelects(response, 'input[name="assigned_to"][value="individual"]')
        assertSoupSelects(response, 'input[name="assigned_to"][value="none"]')

    def test_can_save_preferences(self):
        response = self.client.post(self.url, {'assigned_to': 'none'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your preferences have been saved')

    def test_does_not_update_if_unchanged(self):
        response = self.client.post(self.url, {'assigned_to': 'individual'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No changes were made')

    def tearDown(self):
        self.user.delete()


class ContactInfoUpdateTests(TestCase):

    def setUp(self):
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.form_data = {'type': ContactEditForm.CONTEXT_KEY}

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id})

    def tearDown(self):
        self.user.delete()

    def test_update_name_and_zipcode(self):
        """Contact info updates on successful POST"""
        new_first_name = 'TESTER'
        new_zipcode = '00000'
        self.form_data.update({'contact_first_name': new_first_name})
        self.form_data.update({'contact_zip': new_zipcode})
        response = self.client.post(self.url, self.form_data, follow=True)
        self.assertTrue(response.context['data'].contact_first_name == new_first_name)

        self.test_report.refresh_from_db()
        self.assertEqual(self.test_report.contact_first_name, new_first_name)
        self.assertEqual(self.test_report.contact_zip, new_zipcode)

    def test_no_update_if_validation_fails(self):
        """Contact info not updated if form validation fails
            errors rendered on resulting page
        """
        new_email = 'not an email'
        original_email = self.test_report.contact_email
        self.form_data.update({'contact_email': new_email})
        response = self.client.post(self.url, self.form_data, follow=True)

        self.test_report.refresh_from_db()
        self.assertEqual(self.test_report.contact_email, original_email)

        # Error message rendered on page
        self.assertContains(response, ContactEditForm.FAIL_MESSAGE)


class ReportEditShowViewTests(TestCase):

    def setUp(self):
        self.report_data = SAMPLE_REPORT_1.copy()
        self.report_data.update({'primary_complaint': PRIMARY_COMPLAINT_CHOICES[0][0]})
        self.report = Report.objects.create(**self.report_data)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        self.original_crt_day = self.report_data['crt_reciept_day']
        self.original_crt_month = self.report_data['crt_reciept_month']
        self.original_crt_year = self.report_data['crt_reciept_year']

    def tearDown(self):
        self.user.delete()

    def test_returns_400_if_no_formtype(self):
        """400 error returned if form_type is missing"""
        form_data = {}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 400)

    def test_viewed_in_activity_log(self):
        """Report viewed in activity log on successful GET"""
        response = self.client.get(self.url)
        self.assertTrue('Report viewed:' in str(response.content))
        self.assertFalse('Report opened:' in str(response.content))
        self.assertEqual(response.status_code, 200)

    def test_update_primary_cause(self):
        """Report fields update on successful POST"""
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint}
        response = self.client.post(self.url, form_data, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.primary_complaint, new_primary_complaint)
        self.assertTrue(response.context['data'].primary_complaint == new_primary_complaint)

    def test_excluded_fields_not_modifiable(self):
        """If form data is received outside of scope of ReportEditForm it's not saved"""
        # Contact info
        initial_summary = self.report.violation_summary
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'violation_summary': 'test'}
        response = self.client.post(self.url, form_data, follow=True)

        self.report.refresh_from_db()
        self.assertTrue(response.context['data'].violation_summary == initial_summary)

    def test_only_keep_errors_from_submitted_form(self):
        """If invalid form data is received for multiple forms
           Only report errors for submitted form
           Discard other data

           Here we submit an invalid ReportEditForm, w/ month out of range
           and include post data for a contact information field.

           The resulting rendered page must contain a new ContactEditForm
           and not contain the submitted contact_email data
        """
        initial = self.report.contact_email

        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'last_incident_month': 99, 'contact_email': 'test@'}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.context['contact_form'].initial['contact_email'], initial)

    def test_crt_date_update(self):
        """Update crt receipt date with valid data
        """
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint, 'crt_reciept_month': 12, 'crt_reciept_day': 3, 'crt_reciept_year': 2001}
        response = self.client.post(self.url, form_data, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.primary_complaint, new_primary_complaint)
        self.assertTrue(response.context['data'].primary_complaint == new_primary_complaint)
        self.assertEqual(self.report.crt_reciept_month, 12)
        self.assertTrue(response.context['data'].crt_reciept_month == 12)
        self.assertEqual(self.report.crt_reciept_day, 3)
        self.assertTrue(response.context['data'].crt_reciept_day == 3)
        self.assertEqual(self.report.crt_reciept_year, 2001)
        self.assertTrue(response.context['data'].crt_reciept_year == 2001)

    def test_crt_month_validation(self):
        """Update crt receipt date with bad month. Nothing should be updated.
        """
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint, 'crt_reciept_month': 0, 'crt_reciept_day': 3, 'crt_reciept_year': 2001}
        response = self.client.post(self.url, form_data, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.crt_reciept_month, self.original_crt_month)
        self.assertEqual(self.report.crt_reciept_day, self.original_crt_day)
        self.assertEqual(self.report.crt_reciept_year, self.original_crt_year)
        self.assertTrue('Failed to update complaint details.' in str(response.content))

    def test_crt_day_validation(self):
        """Update crt receipt date with bad day. Nothing should be updated.
        """
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint, 'crt_reciept_month': 12, 'crt_reciept_day': 32, 'crt_reciept_year': 2001}
        response = self.client.post(self.url, form_data, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.crt_reciept_month, self.original_crt_month)
        self.assertEqual(self.report.crt_reciept_day, self.original_crt_day)
        self.assertEqual(self.report.crt_reciept_year, self.original_crt_year)
        self.assertTrue('Failed to update complaint details.' in str(response.content))

    def test_crt_year_validation(self):
        """Update crt receipt date with bad year. Nothing should be updated.
        """
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint, 'crt_reciept_month': 12, 'crt_reciept_day': 3, 'crt_reciept_year': 1999}
        response = self.client.post(self.url, form_data, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.crt_reciept_month, self.original_crt_month)
        self.assertEqual(self.report.crt_reciept_day, self.original_crt_day)
        self.assertEqual(self.report.crt_reciept_year, self.original_crt_year)
        self.assertTrue('Failed to update complaint details.' in str(response.content))


class CRTReportWizardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('crt_report_form')

    @override_settings(MAINTENANCE_MODE=True)
    def test_returns_503_when_maintenance_mode_true(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)

    def test_returns_200_when_maintenance_mode_false(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ReportAttachmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.report = ReportFactory.create()
        self.pk = self.report.pk
        self.fake_file = io.StringIO('this is a fake file')
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

    @patch('cts_forms.models.ReportAttachment.full_clean')
    def test_post_valid_file(self, mock_validate_file_infection):
        response = self.client.post(
            reverse(
                'crt_forms:save-report-attachment',
                kwargs={'report_id': self.pk}
            ),
            {
                'report': self.pk,
                'file': self.fake_file
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        # there should be a message that the file was attached
        self.assertTrue('Successfully attached file' in str(response.content))
        # the attachment should appear in the activity log
        self.assertTrue('Attached file:' in str(response.content))

    @patch('cts_forms.models.ReportAttachment.full_clean')
    def test_post_invalid_file(self, mock_validate_file_infection):
        mock_validate_file_infection.side_effect = ValidationError('invalid file')
        response = self.client.post(
            reverse(
                'crt_forms:save-report-attachment',
                kwargs={'report_id': self.pk}
            ),
            {
                'report': self.pk,
                'file': self.fake_file
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        # there should be a message that the attachment failed
        self.assertTrue('Could not save attachment: invalid file' in str(response.content))

    def test_get_attachment(self):
        user_specified_filename = 'a'
        internal_filename = 'b'

        file = TemporaryUploadedFile(internal_filename, 'text/plain', 10000, 'utf-8')
        attachment = ReportAttachment.objects.create(file=file, user=self.user, filename=user_specified_filename, report=self.report)
        attachment.save()

        response = self.client.get(
            reverse(
                'crt_forms:get-report-attachment',
                kwargs={'id': self.pk, 'attachment_id': attachment.pk}
            ),
        )

        # we should reply with a redirect to a presigned s3 url
        if (response.status_code == 200):
            return self.skipTest('attachments work')

        self.assertEqual(response.status_code, 302)
        # the presigned url should target the private S3 bucket
        self.assertTrue('/crt-private/' in str(response.url))
        # the presigned url should have a 30 second expiration
        self.assertTrue('Expires=30' in str(response.url))
        # the presigned url should target the internal (not user specified) filename
        self.assertTrue(f'/attachments/{internal_filename}' in str(response.url))
        # the response-content-disposition should be set so that the file downloads with the user specified filename
        self.assertTrue(f'response-content-disposition=attachment%3Bfilename%3D{user_specified_filename}' in str(response.url))

    def test_removed_attachment_not_displaying(self):
        file = TemporaryUploadedFile('internal-filename', 'text/plain', 10000, 'utf-8')
        attachment = ReportAttachment.objects.create(file=file, user=self.user, filename='user_specified_filename', report=self.report)
        attachment.save()

        response = self.client.post(
            reverse(
                'crt_forms:remove-report-attachment',
                kwargs={'attachment_id': attachment.pk}
            ),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        # there should be a message that the file was removed
        self.assertTrue(f'Successfully removed {attachment.filename}' in str(response.content))
        # the file should no longer appear in the attachments list
        self.assertTrue(f'complaint-view-remove-attachment-{attachment.pk}' not in str(response.content))
        # the removal should appear in the activity log
        self.assertTrue('Removed attachment:' in str(response.content))


class Complaint_Show_View_Valid(TestCase):
    def setUp(self):
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'voting'
        data['election_details'] = 'federal'
        data['hate_crime'] = 'yes'

        test_report = Report.objects.create(**data)

        for choice in PROTECTED_MODEL_CHOICES:
            pc = ProtectedClass.objects.get_or_create(value=choice[0])[0]
            test_report.protected_class.add(pc)
            test_report.save()

        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': test_report.id}))
        self.context = response.context
        self.content = str(response.content)
        self.test_report = test_report

    def tearDown(self):
        self.user.delete()

    def test_correspondant_info(self):
        self.assertTrue(self.test_report.contact_email in self.content)
        self.assertTrue(self.test_report.contact_phone in self.content)
        self.assertTrue(self.test_report.contact_first_name in self.content)
        self.assertTrue(self.test_report.contact_last_name in self.content)

    def test_complaint_details(self):
        pc = PRIMARY_COMPLAINT_CHOICES[3][1]
        self.assertTrue(str(pc) in self.content)
        self.assertTrue('Election type (federal/local): federal' in self.content)
        self.assertTrue(self.test_report.hate_crime in self.content)
        self.assertTrue(self.test_report.location_name in self.content)
        self.assertTrue(self.test_report.location_city_town in self.content)
        self.assertTrue(self.test_report.location_state in self.content)

    def test_full_summary(self):
        self.assertTrue(self.test_report.violation_summary in self.content)


class Valid_CRT_Pagnation_Tests(TestCase):
    def setUp(self):
        for choice, label in PROTECTED_MODEL_CHOICES:
            pc = ProtectedClass.objects.get_or_create(value=choice)
            test_report = Report.objects.create(**SAMPLE_REPORT_1)
            test_report.protected_class.add(pc[0])
            test_report.save()

        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.content = str(response.content)

    def tearDown(self):
        self.user.delete()

    def test_total_pages(self):
        # we are making a test record for each protected class
        num_records = len(PROTECTED_MODEL_CHOICES)
        self.assertTrue(f'{num_records} of {num_records} records' in self.content)

    def test_paging(self):
        url_base = reverse('crt_forms:crt-forms-index')
        url = f'{url_base}?page=6&per_page=1&sort=assigned_section'
        response = self.client.get(url)
        content = str(response.content)
        # check first page, current page, and the pages before and after
        self.assertTrue('Go to page 1.' in content)
        self.assertTrue('Go to page 5.' in content)
        self.assertTrue('Current page, page 6.' in content)
        self.assertTrue('Go to page 7.' in content)
        self.assertTrue(f'Go to page {len(PROTECTED_MODEL_CHOICES)}.' in content)
        # link generation, update with sorting etc. as we add
        self.assertTrue('href="?per_page=1' in content)
        self.assertTrue('sort=assigned_section' in content)


class Valid_CRT_SORT_Tests(TestCase):
    def setUp(self):
        for choice in PRIMARY_COMPLAINT_CHOICES:
            SAMPLE_REPORT_1['primary_complaint'] = choice[0]
            test_report = Report.objects.create(**SAMPLE_REPORT_1)
            test_report.assigned_section = test_report.assign_section()
            test_report.save()

        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        url_base = reverse('crt_forms:crt-forms-index')
        url_1 = f'{url_base}?sort=assigned_section'
        url_2 = f'{url_base}?sort=-assigned_section'
        self.response_1 = self.client.get(url_1).content
        self.response_2 = self.client.get(url_2).content

    def tearDown(self):
        self.user.delete()

    def test_default_sort_order_desc(self):
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        expected_list = []
        for record in response.context['data_dict']:
            expected_list.append(record['report'].create_date)

        self.assertTrue(expected_list == sorted(expected_list, key=None, reverse=True))
        self.assertFalse(expected_list == sorted(expected_list))

    def test_sort(self):
        # Vote should come after ADM when alphabetical, opposite for reverse
        vote_index_1 = str(self.response_1).find('VOT')
        adm_index_1 = str(self.response_1).find('ADM')
        self.assertTrue(vote_index_1 > adm_index_1)

    def test_bad_sort_param(self):
        url_base = reverse('crt_forms:crt-forms-index')
        url_3 = f'{url_base}?sort=-assigned_section'
        response_3 = self.client.get(url_3)
        self.assertTrue(response_3.status_code, '404')


class CRT_FILTER_Tests(TestCase):
    def setUp(self):
        for choice in PRIMARY_COMPLAINT_CHOICES:
            SAMPLE_REPORT_1['primary_complaint'] = choice[0]
            test_report = Report.objects.create(**SAMPLE_REPORT_1)
            test_report.assigned_section = test_report.assign_section()
            test_report.save()

        SAMPLE_REPORT_1['primary_complaint'] = PRIMARY_COMPLAINT_CHOICES[0][0]
        test_report = Report.objects.create(**SAMPLE_REPORT_1)
        test_report.contact_first_name = 'Mary'
        test_report.contact_last_name = 'Bar'
        test_report.location_city_town = 'Cleveland'
        test_report.location_state = 'OH'
        test_report.assigned_section = test_report.assign_section()
        test_report.servicemember = 'yes'
        test_report.hate_crime = 'yes'
        test_report.public_id = '999-XYZ'

        self.campaign = Campaign.objects.create(internal_name="Fake Campaign")
        test_report.origination_utm_campaign = self.campaign

        test_report.save()

        self.test_report2 = Report.objects.create(**SAMPLE_REPORT_3)
        self.test_report3 = Report.objects.create(**SAMPLE_REPORT_4)
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.url_base = reverse('crt_forms:crt-forms-index')
        self.len_all_results = len(self.client.get(self.url_base).context['data_dict'])

    def tearDown(self):
        self.user.delete()
        self.campaign.delete()

    def test_filter(self):
        url = f'{self.url_base}?assigned_section=ADM'
        one_filter_response = self.client.get(url)
        expected_reports = Report.objects.filter(assigned_section='ADM')
        actual_reports = one_filter_response.context['data_dict']

        self.assertTrue(len(actual_reports) == len(list(expected_reports)))

    def test_id_filter(self):
        url = f'{self.url_base}?public_id=999-XYZ'
        one_filter_response = self.client.get(url)
        actual_reports = str(one_filter_response.content)
        self.assertTrue('999-XYZ' in actual_reports)

    def test_combined_filter(self):
        url_1 = f'{self.url_base}?assigned_section=ADM&status=new'
        two_filter_response = self.client.get(url_1)
        url_2 = f'{self.url_base}?assigned_section=ADM&status=closed'
        two_filter_no_match = self.client.get(url_2)

        # assumes all new reports are assigned to ADM and labeled new
        all_reports_actual = Report.objects.filter(assigned_section='ADM', status='new')
        all_reports_expected = two_filter_response.context['data_dict']
        # assumes no reports should be assigned to ADM and marked closed
        no_reports_actual = Report.objects.filter(assigned_section='ADM', status='closed')
        no_reports_expected = two_filter_no_match.context['data_dict']

        self.assertTrue(len(all_reports_actual) == len(all_reports_expected))
        self.assertTrue(len(no_reports_actual) == len(no_reports_expected))

    def test_date_filter(self):
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        url_start_yesterday = f"{self.url_base}?create_date_start={yesterday.strftime('%Y-%m-%d')}"
        start_yesterday_response = self.client.get(url_start_yesterday).context['data_dict']

        url_start_tomorrow = f"{self.url_base}?create_date_start={tomorrow.strftime('%Y-%m-%d')}"
        start_tomorrow_response = self.client.get(url_start_tomorrow).context['data_dict']

        url_end_yesterday = f"{self.url_base}?create_date_end={yesterday.strftime('%Y-%m-%d')}"
        end_yesterday_response = self.client.get(url_end_yesterday).context['data_dict']

        url_end_tomorrow = f"{self.url_base}?create_date_end={tomorrow.strftime('%Y-%m-%d')}"
        end_tomorrow_response = self.client.get(url_end_tomorrow).context['data_dict']

        # sanity check
        self.assertTrue(self.len_all_results > 0)

        self.assertEqual(len(start_tomorrow_response), 0)
        self.assertEqual(len(end_yesterday_response), 0)
        self.assertEqual(len(start_yesterday_response), self.len_all_results)
        self.assertEqual(len(end_tomorrow_response), self.len_all_results)

    def test_text_filter(self):
        url_phrase = f'{self.url_base}?violation_summary=Four%20score%20and%20seven'
        phrase_response = self.client.get(url_phrase).context['data_dict']

        url_phrase_case_insensitive = f'{self.url_base}?violation_summary=four%20score%20and%20seven'
        case_insensitive_phrase_response = self.client.get(url_phrase_case_insensitive).context['data_dict']

        url_disjointed_phrase = f'{self.url_base}?violation_summary=For%20seven'
        disjointed_phrase_response = self.client.get(url_disjointed_phrase).context['data_dict']

        url_not_in_phrase = f'{self.url_base}?violation_summary=haberdashery'
        url_not_in_phrase_response = self.client.get(url_not_in_phrase).context['data_dict']

        self.assertEqual(len(phrase_response), 8)
        self.assertEqual(len(case_insensitive_phrase_response), 8)
        self.assertEqual(len(disjointed_phrase_response), 8)
        self.assertEqual(len(url_not_in_phrase_response), 0)

    def test_first_name_filter(self):
        first_name_filter = 'contact_first_name=lin'
        response = self.client.get(f'{self.url_base}?{first_name_filter}')
        reports = response.context['data_dict']
        expected_reports = Report.objects.filter(contact_first_name__icontains='lin').count()

        report_len = len(reports)

        self.assertEqual(report_len, expected_reports)

    def test_campaign_filter(self):
        campaign_filter = 'origination_utm_campaign=Fake%20Campaign'
        response = self.client.get(f'{self.url_base}?{campaign_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 1)

    def test_campaign_filter_none(self):
        campaign_filter = 'origination_utm_campaign=(none)'
        response = self.client.get(f'{self.url_base}?{campaign_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, self.len_all_results - 1)

    def test_campaign_filter_invalid(self):
        campaign_filter = 'origination_utm_campaign=woops'
        response = self.client.get(f'{self.url_base}?{campaign_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 0)

    def test_last_name_filter(self):
        last_name_filter = 'contact_last_name=bar'
        response = self.client.get(f'{self.url_base}?{last_name_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 1)

    def test_city_name_filter(self):
        city_name_filter = 'location_city_town=land'
        response = self.client.get(f'{self.url_base}?{city_name_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 1)

    def test_state_filter(self):
        state_filter = 'location_state=OH'
        response = self.client.get(f'{self.url_base}?{state_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 1)

    def test_summary_filter(self):
        """This is a many to may field so it works differently than the other searches. Also checking stemming"""
        summary = CommentAndSummary.objects.create(
            note="service animal",
            is_summary=True,
        )
        test_report = Report.objects.all()[0]
        test_report.internal_comments.add(summary)

        summary_filter = 'summary=service animals'
        response = self.client.get(f'{self.url_base}?{summary_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEqual(report_len, 1)

    def test_servicemember_filter(self):
        servicemember_filter = 'servicemember=yes'
        response = self.client.get(f'{self.url_base}?{servicemember_filter}')
        reports = response.context['data_dict']
        expected_reports = Report.objects.filter(servicemember='yes').count()

        report_len = len(reports)

        self.assertEqual(report_len, expected_reports)

    def test_hatecrime_filter(self):
        filter_ = 'hate_crime=yes'
        response = self.client.get(f'{self.url_base}?{filter_}')
        reports = response.context['data_dict']
        expected_reports = Report.objects.filter(hate_crime='yes').count()

        report_len = len(reports)

        self.assertEqual(report_len, expected_reports)

    def test_profile_filters(self):
        """
        Results filtered by assigned_section set in profile if no assigned_section provided
        """
        Profile.objects.create(intake_filters='IER', user_id=self.user.id)
        response = self.client.get(f'{self.url_base}')
        reports = response.context['data_dict']

        # No IER reports exist so none should be returned when our profile is set to
        self.assertEqual(Report.objects.filter(assigned_section='IER').count(), 0)
        self.assertEqual(len(reports), 0)

    def test_profile_filters_override(self):
        """
        Results filtered by provided assigned_section, bypassing profile filter
        """
        Profile.objects.create(intake_filters='IER', user_id=self.user.id)
        filter_ = 'assigned_section=ADM'
        response = self.client.get(f'{self.url_base}?{filter_}')
        reports = response.context['data_dict']

        # We've specified ADM as a query param, we should only see reports from that section
        expected_reports = Report.objects.filter(assigned_section='ADM').count()
        self.assertEqual(len(reports), expected_reports)

    def test_grouping_filter(self):
        grouping_filter = 'grouping=matching-descriptions'
        response = self.client.get(f'{self.url_base}?{grouping_filter}')
        groups = response.context['groups']
        self.assertEqual(len(groups), 2)
        self.assertTrue('Group 1' in str(response.content))


class Data_Export(TestCase):
    def setUp(self):
        call_command('generate_yearly_reports')
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.url = reverse('crt_forms:get-report-data')

    def test_get_reports_unauthenticated(self):
        """Unauthenticated attempt to view all page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_reports(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reports-data-2020.csv' in str(response.content))
        self.assertTrue('reports-data-2021.csv' in str(response.content))
        self.assertTrue('reports-data-2022.csv' in str(response.content))


class CRT_Dashboard_Tests(TestCase):
    def setUp(self):
        # We'll need a report and a handful of actions
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.superuser2 = User.objects.create_superuser('superduperuser2', 'a@a.com', '')
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
        self.report2 = Report.objects.create(**SAMPLE_REPORT_1)
        self.url = reverse('crt_forms:dashboard')

        [add_activity(self.superuser, 'verb', 'description', self.report) for _ in range(5)]
        [add_activity(self.superuser, 'verb', 'description_2', self.report) for _ in range(5)]

    def test_view_dashboard_unauthenticated(self):
        """Unauthenticated attempt to view all page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_dashboard_authenticated(self):
        """Authenticated will return 200 and display "No records found."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Select intake specialist' in str(response.content))

    def test_assigned_to_filter_wrong_user(self):
        url = f'{self.url}?assigned_to=superduperuser2'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('0 reports' in str(response.content))
        self.assertTrue('superduperuser2' in str(response.content))

    def test_assigned_to_filter(self):
        """Should only return one report even though that report has two activities associated with it"""
        url = f'{self.url}?assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('1 report' in str(response.content))
        self.assertTrue('superduperuser' in str(response.content))

    def test_date_range(self):
        url = f'{self.url}?create_date_start=2021-09-01&create_date_end=2035-09-30&assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('1 report' in str(response.content))

    def test_add_activity_to_new_report(self):
        url = f'{self.url}?create_date_start=2021-09-01&create_date_end=2035-09-30&assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        [add_activity(self.superuser, 'verb', 'description', self.report2) for _ in range(5)]
        response = self.client.get(url)
        self.assertTrue('2 reports' in str(response.content))

    def test_bad_start_date_range(self):
        url = f'{self.url}?create_date_start=2030-09-01&assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('0 reports' in str(response.content))

    def test_bad_end_date(self):
        url = f'{self.url}?create_date_end=2016-09-01&assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('0 reports' in str(response.content))


class CRT_Activity_Dashboard_Tests(TestCase):
    def setUp(self):
        # We'll need a report and a handful of actions
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.superuser2 = User.objects.create_superuser('superduperuser2', 'a@a.com', '')
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
        self.report2 = Report.objects.create(**SAMPLE_REPORT_1)
        self.url = reverse('crt_forms:activity-log')
        add_activity(self.superuser, 'Added comment: ', 'description', self.report)
        add_activity(self.superuser, 'Added summary: ', 'description', self.report)

    def test_view_activity_dashboard_unauthenticated(self):
        """Unauthenticated attempt to view all page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_activity_dashboard_authenticated(self):
        """Authenticated will return 200 and display "Select intake specialist."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Select intake specialist' in str(response.content))

    def test_assigned_to_filter_wrong_user(self):
        url = f'{self.url}?assigned_to=superduperuser2'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('0 records' in str(response.content))
        self.assertTrue('superduperuser2' in str(response.content))

    def test_assigned_to_filter(self):
        """Should only return two records for the report"""
        url = f'{self.url}?assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('2 records' in str(response.content))
        self.assertTrue('superduperuser' in str(response.content))

    def test_date_range(self):
        url = f'{self.url}?create_date_start=2021-09-01&create_date_end=2035-09-30&assigned_to=superduperuser'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('2 records' in str(response.content))

    def test_verb_filter(self):
        url = f'{self.url}?create_date_start=2021-09-01&create_date_end=2035-09-30&assigned_to=superduperuser&actions=Added summary: '
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('1 record' in str(response.content))

    def test_complaint_id_filter(self):
        url = f'{self.url}?create_date_start=2021-09-01&create_date_end=2035-09-30&assigned_to=superduperuser&public_id={self.report.id}'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('2 records' in str(response.content))


class CRT_Saved_Search_Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.ADMsavedSearch = SavedSearch.objects.create(
            name="ADM Saved Search",
            query="status=closed&grouping=default",
            section="ADM",
            shared=True
        )
        self.CRMsavedSearch = SavedSearch.objects.create(
            name="CRM Saved Search",
            query="status=open&grouping=default",
            section="CRM",
            shared=True
        )
        self.url = reverse('crt_forms:saved-searches')

    def test_view_saved_search_unauthenticated(self):
        """Unauthenticated attempt to view saved search page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_saved_search_authenticated(self):
        """Authenticated will return 200 and display both saved searches."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('ADM Saved Search' in str(response.content))
        self.assertTrue('CRM Saved Search' in str(response.content))

    def test_section_filter(self):
        url = f'{self.url}?section_filter=ADM'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertTrue('ADM Saved Search' in str(response.content))
        self.assertFalse('CRM Saved Search' in str(response.content))


class CRT_Saved_Search_Action_Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.ADMsavedSearch = SavedSearch.objects.create(
            name="ADM Saved Search",
            query="status=closed&grouping=default",
            section="ADM",
        )
        self.url = reverse('crt_forms:saved-search-actions')

    def test_view_saved_search_actions_unauthenticated(self):
        """Unauthenticated attempt to view saved search action page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_add_saved_search_actions_authenticated(self):
        """Authenticated will return 200 and display create save search action page."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Add new saved search' in str(response.content))

    def test_view_update_saved_search_actions_authenticated(self):
        """Authenticated will return 200 and display update saved search action page."""
        self.client.force_login(self.superuser)
        url = reverse('crt_forms:saved-search-actions', kwargs={'id': self.ADMsavedSearch.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Update saved search' in str(response.content))


class CRTDispositionTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.other_report_data = SAMPLE_REPORT_1.copy()
        self.other_report_data.update({'status': 'closed'})
        self.other_report_data.update({'closed_date': date.today()})
        other_retention_schedule = RetentionSchedule.objects.get(retention_years=10)
        self.other_report_data.update({'retention_schedule': other_retention_schedule})
        self.other_report = Report.objects.create(**self.other_report_data)
        self.other_report_data_2 = SAMPLE_REPORT_1.copy()
        self.other_report_data_2.update({'status': 'closed'})
        self.other_report_data_2.update({'closed_date': date.today()})
        other_retention_schedule_2 = RetentionSchedule.objects.get(retention_years=3)
        self.other_report_data_2.update({'retention_schedule': other_retention_schedule_2})
        self.other_report_2 = Report.objects.create(**self.other_report_data_2)
        self.expired_report_data = SAMPLE_REPORT_1.copy()
        self.expired_report_data.update({'status': 'closed'})
        self.expired_report_data.update({'closed_date': "2020-02-01 18:17:52.74131+00"})
        expired_retention_schedule = RetentionSchedule.objects.get(retention_years=1)
        self.expired_report_data.update({'retention_schedule': expired_retention_schedule})
        self.expired_report = Report.objects.create(**self.expired_report_data)
        self.url = reverse('crt_forms:disposition')

    def test_view_disposition_unauthenticated(self):
        """Unauthenticated attempt to view all page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_disposition_authenticated(self):
        """Authenticated will return 200 and display "Disposing Report Records"""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Disposing Report Records', str(response.content))

    def test_past_disposition(self):
        url = f'{self.url}?disposition_status=past'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        reports = response.context['data_dict']
        report_len = len(reports)
        self.assertEqual(report_len, 1)
        self.assertIn('1 Year', str(response.content))

    def test_other_scheduled_reports(self):
        """Should only return two reports, with three year and ten year"""
        url = f'{self.url}?disposition_status=other'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        reports = response.context['data_dict']
        report_len = len(reports)
        self.assertEqual(report_len, 2)
        self.assertIn('3 Year', str(response.content))
        self.assertIn('10 Year', str(response.content))

    def test_filter_by_schedule(self):
        """Should only return two reports, with three year and ten year"""
        url = f'{self.url}?disposition_status=other&retention_schedule=10%20Year'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        reports = response.context['data_dict']
        report_len = len(reports)
        self.assertEqual(report_len, 1)
        self.assertIn('10 Year', str(response.content))

    def test_filter_by_expiration(self):
        """Should only return two reports, with three year and ten year"""
        year = date.today().year + 4
        url = f'{self.url}?disposition_status=other&expiration_date={year}-01-01'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        reports = response.context['data_dict']
        report_len = len(reports)
        self.assertEqual(report_len, 1)
        self.assertIn('10 Year', str(response.content))

    def test_disposition_bulk_action(self):
        url = reverse('crt_forms:disposition-actions')
        url = f'{url}?next=%253Fper_page%253D15%2526status%253Dclosed%2526retention_schedule%253D1%2520Year%2526retention_schedule%253D3%2520Year%2526retention_schedule%253D10%2520Year%2526retention_schedule%253DPermanent%2526disposition_status%253Dpast%2526page%253D1&id={self.other_report.id}&id={self.other_report_2.id}'
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertIn('disposal', str(response.content))


class LoginRequiredTests(TestCase):
    """Please add a test for each url that is tied to a view that requires authorization/authentication."""

    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'lennon@thebeatles.com', self.test_pass)
        test_report = Report.objects.create(**SAMPLE_REPORT_1)
        test_report.save()
        self.report = test_report

    def tearDown(self):
        self.user.delete()

    def test_view_all_login_success(self):
        """Successful login returns 200 success code."""
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.assertEqual(response.status_code, 200)

    def test_view_all_unauthenticated(self):
        """Unauthenticated attempt to view all page redirects to login page."""
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/view/')

        response = self.client.get(reverse('crt_forms:crt-pro-form'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/new/')

        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/view/1/')

        response = self.response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': 1}
            ),
            {
                'is_summary': False,
                'note': 'hello',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/comment/report/1/')

    def test_view_report_details_authenticated(self):
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_report_details_unauthenticated(self):
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id}))
        expected_response = '/accounts/login/?next=/form/view/%s/' % self.report.id
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_response)

    def test_view_all_incorrect_password(self):
        """Attempt with incorrect password redirects to login page."""
        self.client.login(username='DELETE_USER', password='incorrect_password')  # nosec -- this code runs in test only
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/view/')

    def test_required_user_logging(self):
        """For compliance and good forensics, check a sample of required logging events"""
        with LogCapture() as cm:
            self.client = Client()
            self.test_pass = secrets.token_hex(32)
            self.user2 = User.objects.create_user('DELETE_USER_2', 'mccartney@thebeatles.com', self.test_pass)
            self.user2_pk = copy.copy(self.user2.pk)
            self.user2.delete()

            create = 'cts_forms.signals', 'INFO', 'ADMIN ACTION by: CLI CLI @ CLI User created: {pk} permissions: <QuerySet []> staff: False superuser: False active: True'.format(pk=self.user2_pk)
            self.assertEqual(
                cm.check_present(
                    (create)
                ),
                None,
            )

            delete = 'cts_forms.signals', 'INFO', 'ADMIN ACTION by: CLI CLI @ CLI User deleted: {pk} permissions: <QuerySet []> staff: False superuser: False active: True'.format(pk=self.user2_pk)
            self.assertEqual(
                cm.check_present(
                    (delete)
                ),
                None,
            )


class ReportEditApiTests(TestCase):

    report_data = {
        "contact_first_name": "fakefirst",
        "contact_last_name": "fakelast",
        "contact_phone": "+15555555555",
        "contact_email": "fake@example.com",
        "contact_address_line_1": "123 Fake St",
        "contact_address_line_2": "",
        "contact_city": "Fakington",
        "contact_state": "OH",
        "contact_zip": "12345",
        "primary_complaint": "voting",
        "location_name": "Fake Org",
        "location_address_line_1": "1234 Fake Ave",
        "location_address_line_2": "",
        "location_city_town": "Fakeville",
        "location_state": "AZ",
        "violation_summary": "something happened",
        "crt_reciept_month": 8,
        "crt_reciept_day": 15,
        "crt_reciept_year": 2024,
        "intake_format": "phone",
    }

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "user@example.com", "")
        self.base_url = reverse('api:report-edit')
        self.client.login(username="USER_1", password="")  # nosec

    def tearDown(self):
        self.user.delete()

    def test_phone_pro_form_404s(self):
        url = self.base_url

        response = self.client.post(url,
                                    {'public_id': 'not-a-public-id'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 404)

    def test_phone_pro_form_creates(self):
        url = self.base_url

        # Just the subset from the phone pro form:
        response = self.client.post(url, self.report_data, content_type='application/json')
        response_json = response.json()

        public_id = response_json['form']['public_id']
        pk = public_id.split('-')[0]
        self.assertGreater(int(pk), 0)
        self.assertEqual(response.status_code, 201)
        self.maxDiff = None
        self.assertDictEqual(response_json, {
            'changed_data': ['contact_first_name',
                             'contact_last_name',
                             'contact_phone',
                             'contact_email',
                             'contact_address_line_1',
                             'contact_city',
                             'contact_state',
                             'contact_zip',
                             'primary_complaint',
                             'location_name',
                             'location_address_line_1',
                             'location_city_town',
                             'location_state',
                             'violation_summary',
                             'crt_reciept_month',
                             'crt_reciept_day',
                             'crt_reciept_year',
                             'intake_format',
                             'public_id'],
            'form': {
                **self.report_data,
                'public_id': public_id,
            },
            'messages': [
                {'message': f'Successfully created report {public_id}',
                 'type': 'success'},
            ],
            'new_url': f'/form/new/phone/{pk}/',
        })

    def test_phone_pro_form_edits(self):
        public_id = '123-XYZ'
        report = Report.objects.create(**self.report_data)
        report.public_id = public_id
        report.save()
        url = self.base_url

        # Just the subset from the phone pro form:
        response = self.client.post(url,
                                    {
                                        'public_id': public_id,
                                        **self.report_data,
                                        'contact_first_name': 'newfirst',
                                    },
                                    content_type='application/json')
        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.maxDiff = None
        self.assertDictEqual(response_json, {
            'changed_data': ['contact_first_name'],
            'form': {
                **self.report_data,
                'contact_first_name': 'newfirst',
                'public_id': public_id,
            },
            'messages': [
                {'message': 'Contact first name: Updated from "fakefirst" to "newfirst"',
                 'type': 'success'},
                {'message': f'Successfully updated report {public_id}',
                 'type': 'success'},
            ],
            'new_url': None,
        })


class ReportSummaryApiTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "cookiemonster@fake.net", "")
        self.test_reports = [Report.objects.create(**SAMPLE_REPORT_1) for i in range(10)]
        self.report_ids = [report.id for report in self.test_reports]
        self.base_url = reverse('api:report-summary')
        self.client.login(username="USER_1", password="")  # nosec

    def tearDown(self):
        self.user.delete()

    def test_unauthenticated_user_cant_access_url(self):
        self.client.logout()
        url = self.base_url

        data = {'assigned_section': 'ADM'}

        response = self.client.get(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_filters_count(self):
        url = self.base_url
        self.test_reports[0].assigned_section = 'APP'
        self.test_reports[0].save()

        data = {'assigned_section': 'ADM'}

        response = self.client.get(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"report_count": 9})


class ReportListApiTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "cookiemonster@fake.net", "")
        self.test_reports = [Report.objects.create(**SAMPLE_REPORT_1) for i in range(10)]
        self.report_ids = [report.id for report in self.test_reports]
        self.base_url = reverse('api:report-list')
        self.client.login(username="USER_1", password="")  # nosec

    def tearDown(self):
        self.user.delete()

    def test_unauthenticated_user_cant_access_url(self):
        self.client.logout()
        url = self.base_url

        data = json.dumps({'report_pks': self.report_ids})

        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_url(self):
        url = self.base_url

        data = json.dumps({'report_pks': self.report_ids})
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_missing_list_json(self):
        url = self.base_url

        response = self.client.post(url, json.dumps({}), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_mark_reports_viewed(self):
        url = self.base_url

        data = json.dumps({'report_pks': self.report_ids})
        response = self.client.post(url, data, content_type='application/json')

        for report in self.test_reports:
            report.refresh_from_db()
            self.assertTrue(report.viewed)
        self.assertEqual(response.status_code, 200)


class BannerMessageTests(TestCase):
    """Tests the db-backed banner messages.

    Find more banner tests in the e2e suite."""

    def setUp(self):
        self.client = Client()

    def test_renders_without_banner(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Have you been a victim of a hate crime')

    def test_renders_banner(self):
        BannerMessage.objects.create(show=True,
                                     order=0,
                                     kind='notice',
                                     markdown_content={'en': 'banner **test**'})
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'banner <strong>test</strong>')


class PrintableFormTests(TestCase):
    """Makes sure that the printable PDF form is generated correctly."""

    def test_produces_pdf(self):
        client = Client()
        response = client.get('/report/printable/', follow=True)
        form = pypdf.PdfReader(io.BytesIO(response.content))
        page1 = form.pages[0].extract_text()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'filename="file_a_complaint.pdf"',
            response.get('Content-Disposition')
        )
        self.assertIn('If you believe you or someone else', page1)
        self.assertIn('Are you now or have ever', page1)


class FormLettersIndexTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "cookiemonster@fake.net", "")
        self.base_url = reverse('api:form-letters')
        self.client.login(username="USER_1", password="")  # nosec

    def tearDown(self):
        self.user.delete()

    def test_unauthenticated_user_cant_access_url(self):
        self.client.logout()
        url = f'{self.base_url}?assigned_section=CRM'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_url(self):
        url = f'{self.base_url}?assigned_section=CRM'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_format(self):
        url = f'{self.base_url}?assigned_section=CRM&start_date=4-12-2022&end_date=4-13-2022'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


class CRT_Resource_Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('superduperuser', 'a@a.com', '')
        self.tag = Tag.objects.create(name='test tag', section='DRS', show_in_lists=True)
        self.tag2 = Tag.objects.create(name='test tag 2', section='DRS', show_in_lists=True)
        self.resource = Resource.objects.create(name="Legal Resource", section="DRS", url="www.resource.test")
        self.resource.tags.add(self.tag)
        self.resource.save()
        self.resource2 = Resource.objects.create(name="Technology Resource", section="DRS", url="www.resource2.test")
        self.resource2.tags.add(self.tag2)
        self.resource2.save()
        self.resource3 = Resource.objects.create(name="Housing Resource", section="DRS", url="www.resource3.test")
        self.url = reverse('crt_forms:resources')
        self.resource_api_url = reverse('api:resources-list')

    def test_view_resources_unauthenticated(self):
        """Unauthenticated attempt to view resource page redirects to login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_resources_authenticated(self):
        """Authenticated will return 200 and display "Resources."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Resources' in str(response.content))

    def test_tag_filter(self):
        """Should only return two resources"""
        self.client.force_login(self.superuser)
        api_response = self.client.get(f'{self.resource_api_url}?tag={self.tag.pk}&tag={self.tag2.pk}', content_type='application/json')
        self.assertTrue('1 to 2 of 2 resources' in str(api_response.json()['html']))

    def test_search(self):
        """Should only return one resource"""
        self.client.force_login(self.superuser)
        api_response = self.client.get(f'{self.resource_api_url}?search_term=legal', content_type='application/json')
        self.assertTrue('1 to 1 of 1 resources' in str(api_response.json()['html']))
