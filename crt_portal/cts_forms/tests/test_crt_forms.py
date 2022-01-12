"""
These are the forms that appear on the individual report page to update a report.
See test_intake_forms.py for tests of the general form and the pro form.
"""
import secrets
import urllib.parse

from django.contrib.auth.models import User
from django.http import QueryDict
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import urlencode

from datetime import datetime

from ..forms import BulkActionsForm, ComplaintActions, Filters, ReportEditForm
from ..model_variables import PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, NEW_STATUS
from ..models import CommentAndSummary, Report, ResponseTemplate, EmailReportCount
from .factories import ReportFactory
from .test_data import SAMPLE_REPORT, SAMPLE_RESPONSE_TEMPLATE


class ActionTests(TestCase):
    def setUp(self):
        self.test_pass = secrets.token_hex(32)

        self.user1 = User.objects.create_user('USER_1', 'user1@example.com', self.test_pass)
        self.user2 = User.objects.create_user('USER_2', 'user2@example.com', self.test_pass)

    def test_valid(self):
        form = ComplaintActions(data={
            'assigned_section': 'ADM',
            'status': 'new',
            'primary_statute': '144',
            'district': '1',
        })
        self.assertTrue(form.is_valid())

    def test_user_assignment(self):
        form = ComplaintActions(
            initial={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': self.user1.pk
            },
            data={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': self.user2.pk
            }
        )

        self.assertTrue(form.is_valid())

        for action in form.get_actions():
            self.assertEqual(action[0], 'Assigned to:')
            self.assertEqual(action[1], f'Updated from "{self.user1.username}" to "{self.user2.username}"')

    def test_user_new_assignment(self):
        form = ComplaintActions(
            initial={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': None,
            },
            data={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': self.user2.pk,
            }
        )

        self.assertTrue(form.is_valid())

        self.assertTrue(form.is_valid())
        actions = list(form.get_actions())
        self.assertTrue(actions)
        self.assertEqual(actions[0], ('Assigned to:', f'"{self.user2.username}"'))
        self.assertEqual(actions[1], ('Assigned to:', f'Updated from "None" to "{self.user2.username}"'))

    def test_section_change(self):
        """Changes to section are recorded in activity log"""
        form = ComplaintActions(
            initial={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': self.user1.pk
            },
            data={
                'assigned_section': 'VOT',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': self.user1.pk
            }
        )

        self.assertTrue(form.is_valid())
        actions = list(form.get_actions())
        self.assertTrue(actions)
        self.assertEqual(actions[0], ('Assigned section:', 'Updated from "ADM" to "VOT"'))

    def test_referral(self):
        form = ComplaintActions(
            initial={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': None,
                'referred': False,
            },
            data={
                'assigned_section': 'ADM',
                'status': 'new',
                'primary_statute': '144',
                'district': '1',
                'assigned_to': None,
                'referred': True,
            }
        )
        self.assertTrue(form.is_valid())
        actions = list(form.get_actions())
        self.assertTrue(actions)
        self.assertEqual(actions[0], ('Secondary review:', 'Updated from "False" to "True"'))


class CommentActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

        self.note = 'Important note'
        self.report = ReportFactory.create()
        self.pk = self.report.pk
        self.response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk},
            ),
            {
                'is_summary': False,
                'note': self.note,
                'next': '?per_page=15',
            },
            follow=True
        )

    def test_post(self):
        """A logged in user can post a comment"""
        self.assertEqual(self.response.status_code, 200)

    def test_retain_query(self):
        """if the user came to the page with query parameters, keep them for the back to all button."""
        self.assertTrue('?per_page=15' in str(self.response.content))

    def test_creates_comment(self):
        """A comment is created and associated with the right report"""
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        report = Report.objects.filter(internal_comments__pk=comment_id)[0]
        self.assertEqual(report.pk, self.pk)

    def test_adds_comment_to_activity(self):
        """The comment shows up in the report's activity log"""
        response = self.client.get(
            reverse(
                'crt_forms:crt-forms-show',
                kwargs={'id': self.pk}),
        )
        content = str(response.content)
        self.assertTrue(self.note in content)

    def test_edit_summary(self):
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        update = 'updated note'
        response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk},
            ),
            {
                'is_summary': False,
                'note': update,
                'comment_id': comment_id,
            },
            follow=True
        )
        content = str(response.content)
        self.assertTrue('updated note' in content)

    def test_comment_overflow(self):
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        too_many_words = 'la la la ' * 2500
        response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk},
            ),
            {
                'is_summary': False,
                'note': too_many_words,
                'comment_id': comment_id,
            },
            follow=True
        )
        content = str(response.content)
        self.assertTrue('Could not save comment' in content)
        self.assertEqual(response.status_code, 200)


class ReportEditFormTests(TestCase):
    def setUp(self):
        self.report_data = SAMPLE_REPORT.copy()
        self.report_data.update({'primary_complaint': 'workplace',
                                 'public_or_private_employer': PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES[0][0]})
        self.report = Report.objects.create(**self.report_data)

    def test_changed_data_hate_crime(self):
        data = self.report_data.copy()
        data.update({'hate_crime': 'yes'})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertTrue('hate_crime' in form.changed_data)

    def test_clean_dependent_fields(self):
        """
        On clean, dependent fields of non-selected primary_complaint are set to ""
        Only fields previously containing values are included in changed_data
        """
        data = self.report_data.copy()
        new_primary_complaint = 'housing'
        data.update({'primary_complaint': new_primary_complaint})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('public_or_private_employer' in form.changed_data)
        self.assertTrue('employer_size' not in form.changed_data)
        for field in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS['workplace']:
            self.assertTrue(form.cleaned_data[field] == "")

    def test_summary_can_be_created(self):
        """
        Saving of a valid form instance creates an associated
        CommentAndSummary object w/ is_summary is True
        """
        data = self.report_data.copy()
        new_summary = 'summarized'
        data.update({'summary': new_summary})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('summary' in form.changed_data)

        form.save()
        self.report.refresh_from_db()
        self.assertEqual(self.report.get_summary.note, new_summary)

    def test_summary_can_be_updated(self):
        """
        Saving of a valid form instance updates the associated
        CommentAndSummary object w/ is_summary is True
        """
        # Create and add a summary to our test report
        summary, _ = CommentAndSummary.objects.get_or_create(note='summary', is_summary=True)
        self.report.internal_comments.add(summary)

        data = self.report_data.copy()
        new_summary = 'newest summary'
        data.update({'summary': new_summary, 'summary_id': summary.id})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('summary' in form.changed_data)

        form.save()

        self.report.refresh_from_db()
        summary.refresh_from_db()
        self.assertEqual(self.report.get_summary.note, new_summary)
        self.assertEqual(summary.note, new_summary)

    def test_location_address_can_be_updated(self):
        data = self.report_data.copy()

        # Initialize our report with these addresses
        data.update({
            'location_address_line_1': 'location address 1',
            'location_address_line_2': 'location address 2',
        })
        report = Report.objects.create(**data)

        # Update our location address lines for a Form instance
        data.update({
            'location_address_line_1': 'NEW address 1',
            'location_address_line_2': 'NEW address 2',
        })
        form = ReportEditForm(data, instance=report)
        self.assertTrue(form.is_valid())

        form.save()
        report.refresh_from_db()

        self.assertEqual(report.location_address_line_1, 'NEW address 1')
        self.assertEqual(report.location_address_line_2, 'NEW address 2')


class ResponseActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT)
        self.template = ResponseTemplate.objects.create(**SAMPLE_RESPONSE_TEMPLATE)

    def post_template_action(self, what):
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'templates': self.template.id,
                'type': what,
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        return str(response.content)

    def test_response_action_print(self):
        content = self.post_template_action('print')
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Contacted complainant:' in content)
        self.assertTrue(escape(f"Printed '{self.template.title}' template") in content)

    def test_response_action_copy(self):
        content = self.post_template_action('copy')
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Contacted complainant:' in content)
        self.assertTrue(escape(f"Copied '{self.template.title}' template") in content)

    def test_response_action_blank_submit(self):
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('?per_page=15' in content)
        self.assertFalse('Contacted complainant:' in content)

    def test_create_date_is_EST(self):
        # Add datetime without timezone to make sure its converted to EST
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.save()
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 31, 2020' in content)
        self.assertFalse('You contacted the Department of Justice on January 1, 2021' in content)

    def test_ignore_crt_receipt_date(self):
        # Ignore crt_reciept_date because intake_format is web
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.intake_format = 'web'
        self.report.save()
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 31, 2020' in content)
        self.assertFalse('You contacted the Department of Justice on December 1, 2000' in content)

    def test_bad_crt_receipt_date(self):
        # Ignore crt_reciept_date it is not valid
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.crt_reciept_day = None
        self.report.intake_format = 'fax'
        self.report.save()
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 31, 2020' in content)
        self.assertFalse('You contacted the Department of Justice on December 1, 2000' in content)

    def test_crt_receipt_date(self):
        # use crt_reciept_date
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.intake_format = 'fax'
        self.report.save()
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 1, 2000' in content)
        self.assertFalse('You contacted the Department of Justice on December 31, 2020' in content)


class FormNavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.filter_section = 'ADM'
        self.reports = ReportFactory.create_batch(3, assigned_section=self.filter_section)
        ReportFactory.create_batch(2, assigned_section='CRM')
        ReportFactory.create_batch(2, assigned_section='DRS')
        ReportFactory.create_batch(2, assigned_section='ELS')
        ReportFactory.create_batch(1, assigned_section='EOS')
        EmailReportCount.refresh_view()

    def test_basic_navigation(self):
        first = self.reports[-1]
        response = self.client.get(
            reverse('crt_forms:crt-forms-show', kwargs={'id': first.id}),
            {
                'next': f'?per_page=15&assigned_section={self.filter_section}',
                'index': '0',
            },
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('1 of 3 records' in content)
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[1].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url}?next={next_qp}&index=1") in content)
        self.assertEqual(content.count('complaint-nav'), 2)
        self.assertEqual(content.count('disabled-nav'), 1)

    def test_invalid_index_navigation(self):
        second = self.reports[1]
        response = self.client.get(
            reverse('crt_forms:crt-forms-show', kwargs={'id': second.id}),
            {
                'next': f'?per_page=15&assigned_section={self.filter_section}',
                'index': '5000',
            },
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('2 of 3 records' in content)
        url1 = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[2].id})
        url2 = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[0].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url1}?next={next_qp}&index=0") in content)
        self.assertTrue(escape(f"{url2}?next={next_qp}&index=2") in content)
        self.assertEqual(content.count('complaint-nav'), 2)
        self.assertEqual(content.count('disabled-nav'), 0)

    def test_report_out_of_query_filter(self):
        second = self.reports[1]
        response = self.client.post(
            reverse('crt_forms:crt-forms-show', kwargs={'id': second.id}),
            {
                'next': f'?per_page=15&assigned_section={self.filter_section}',
                'index': '1',
                'type': ComplaintActions.CONTEXT_KEY,
                'assigned_section': 'DRS',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('N/A of 2 records' in content)
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[0].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url}?next={next_qp}&index=1") in content)
        self.assertEqual(content.count('complaint-nav'), 2)
        self.assertEqual(content.count('disabled-nav'), 1)

    def test_email_filtering(self):
        # generate random reports associated with a different email address
        ReportFactory.create_batch(5, assigned_section='VOT', contact_email='SomeoneElse@usa.gov')

        first = self.reports[-1]
        response = self.client.post(
            reverse('crt_forms:crt-forms-show', kwargs={'id': first.id}),
            {
                'next': '?per_page=15&contact_email=SomeoneElse@usa.gov',
                'index': '1',
                'type': ComplaintActions.CONTEXT_KEY,
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('N/A of 5 records' in str(response.content))

    def test_email_count_sorting_asc(self):
        # generate report wiht no email address
        report = ReportFactory.create(contact_email=None)

        response = self.client.post(
            reverse('crt_forms:crt-forms-show', kwargs={'id': report.id}),
            {
                'next': '?per_page=15&sort=email_count',
                'index': '1',
                'type': ComplaintActions.CONTEXT_KEY,
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        # the report with no email should land at the back
        self.assertTrue('11 of 11 records' in str(response.content))

    def test_email_count_sorting_desc(self):
        # generate report wiht no email address
        report = ReportFactory.create(contact_email=None)

        response = self.client.post(
            reverse('crt_forms:crt-forms-show', kwargs={'id': report.id}),
            {
                'next': '?per_page=15&sort=-email_count',
                'index': '1',
                'type': ComplaintActions.CONTEXT_KEY,
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        # the report with no email should land at the back
        self.assertTrue('11 of 11 records' in str(response.content))


class PrintActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT)
        Report.objects.create(**SAMPLE_REPORT)

    def test_response_action_print(self):
        options = ['correspondent', 'activity']
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-print',
                kwargs={'id': self.report.id},
            ),
            {
                'options': options,
                'next': '?per_page=15',
                'index': '22',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Printed report' in content)
        self.assertTrue(escape('Printed correspondent, activity') in content)

    def test_response_action_print_with_ids(self):
        options = ['issue', 'summary']
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-print',
            ),
            {
                'ids': [self.report.id],
                'options': options,
                'modal_next': '?per_page=15',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue(escape('Printed issue, summary for 1 reports') in content)

    def test_response_action_print_all(self):
        options = ['activity', 'issue']
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-print',
            ),
            {
                'type': 'print_all',
                'options': options,
                'modal_next': '?per_page=15',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue(escape('Printed activity, issue for 2 reports') in content)


class ReportActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT, assigned_section='ADM')

    def test_referral_section_checked(self):
        self.assertEqual(self.report.referral_section, '')
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        params = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            'referred': 'on',
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Secondary review:' in content)
        self.assertTrue(escape('Updated from "False" to "True"') in content)
        self.report.refresh_from_db()
        self.assertTrue(self.report.referred)
        self.assertEqual(self.report.referral_section, 'ADM')

    def test_referral_section_unchecked(self):
        self.report.referred = True
        self.report.referral_section = 'ADM'
        self.report.save()
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        params = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            'referred': '',
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Secondary review:' in content)
        self.assertTrue(escape('Updated from "True" to "False"') in content)
        self.report.refresh_from_db()
        self.assertFalse(self.report.referred)
        self.assertEqual(self.report.referral_section, '')

    def test_assign_report_to_user(self):
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        params = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            # Make sure the assigned section is set to the same value.
            # If this assigned section is removed or changed, the assigned_to
            # field doesn't get set.
            'assigned_section': 'ADM',
            'assigned_to': self.user.pk,
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Assigned to:' in content)
        self.assertTrue(escape(f'Updated from "None" to "{self.user.username}"') in content)
        self.report.refresh_from_db()
        self.assertEqual(self.report.assigned_to.pk, self.user.pk)

    def test_unassign_report_to_user(self):
        self.report.assigned_to = self.user
        self.report.save()
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        params = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            'assigned_to': '',
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Assigned to:' in content)
        self.assertTrue(escape(f'Updated from "{self.user.username}" to "None"') in content)
        self.report.refresh_from_db()
        self.assertEqual(self.report.assigned_to, None)


class BulkActionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.reports = ReportFactory.create_batch(16, assigned_section='ADM', status='new')

    def get(self, ids, all_ids=False):
        params = {
            'next': '?per_page=15&status=open&something=else',
            'id': ids,
        }
        if all_ids:
            params['all'] = 'all'
        response = self.client.get(reverse('crt_forms:crt-forms-actions'), params)
        self.assertEqual(response.status_code, 200)
        return response

    def test_get_with_ids(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.get(ids)
        content = str(response.content)
        # verify that all hidden inputs are present with correct values
        next_qp = escape("?per_page=15&status=open&something=else")
        id_str = ",".join([str(id) for id in ids])
        self.assertTrue(f'value="{next_qp}" name="next"' in content)
        self.assertTrue(f'value="{id_str}" name="ids"' in content)
        # bulk assign all options should not show up
        self.assertTrue('value="" name="all"' in content)
        self.assertFalse("button--warning" in content)

    def test_get_with_all(self):
        ids = [report.id for report in self.reports]
        response = self.get(ids, all_ids=True)
        content = str(response.content)
        # verify that all hidden inputs are present with correct values
        next_qp = escape("?per_page=15&status=open&something=else")
        id_str = ",".join([str(id) for id in ids])
        self.assertTrue(f'value="{next_qp}" name="next"' in content)
        self.assertTrue(f'value="{id_str}" name="ids"' in content)
        # bulk assign all options should show up
        self.assertTrue('value="all" name="all"' in content)
        self.assertTrue("button--warning" in content)
        self.assertTrue(f"Apply changes to {len(ids)} records" in content)

    def test_get_with_all_second_page(self):
        ids = [report.id for report in self.reports[8:]]
        params = {
            'next': '?per_page=8',
            'id': ids,
            'all': 'all',
        }
        response = self.client.get(reverse('crt_forms:crt-forms-actions'), params)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        id_str = ",".join([str(id) for id in ids])
        self.assertTrue(f'value="{id_str}" name="ids"' in content)
        self.assertTrue("Print 8 reports" in content)
        self.assertTrue("Print all 16 reports" in content)
        self.assertEqual(content.count('bulk-print-report-extra'), 8)
        # we selected the second page; make sure the first report
        # is marked as "extra" (for print all)
        first_all = content.index('<div class="bulk-print-report bulk-print-report-extra">')
        first_id = content.index('<div class="bulk-print-report">')
        self.assertTrue(first_all > first_id)

    def post(self, ids, all_ids=False, confirm=False, return_url_args='', **extra):
        params = {
            'next': f'?per_page=15&{return_url_args}',
            'ids': ','.join([str(id) for id in ids]),
            **extra,
        }
        if all_ids:
            params['all'] = 'all'
        if confirm:
            params['confirm_all'] = 'confirm_all'
        response = self.client.post(reverse('crt_forms:crt-forms-actions'), params, follow=True)
        self.assertEqual(response.status_code, 200)
        return response

    def test_post_with_invalid_user(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, assigned_to='invalid', comment='a comment')
        content = str(response.content)
        self.assertTrue('Could not bulk update assigned_to: Select a valid choice.' in content)

    def test_post_with_blank_and_invalid_comment(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, comment='')
        content = str(response.content)
        self.assertTrue('Could not bulk update comment: This field is required.' in content)
        response = self.post(ids, comment='a' * 7001)
        content = str(response.content)
        self.assertTrue('Could not bulk update comment: Ensure this value has at most 7000 characters (it has 7001).' in content)

    def test_post_with_ids(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, assigned_to=self.user.id, comment='a comment', assigned_section='ADM', status='new')
        content = str(response.content)
        self.assertTrue('2 records have been updated: assigned to DELETE_USER' in content)
        self.assertEqual(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEqual(last_activity.verb, "Assigned to:")
            self.assertEqual(last_activity.description, 'Updated from "None" to "DELETE_USER"')
            self.assertEqual(last_activity.actor, self.user)

    def test_post_with_section_status_and_assignee(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, assigned_to=self.user.id, comment='a comment', assigned_section='VOT', status='closed')
        content = str(response.content)
        self.assertTrue(escape("2 records have been updated: section set to VOT, status set to new, assigned to '', and primary classification set to ''") in content)
        self.assertEqual(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEqual(last_activity.verb, "Assigned section:")
            self.assertEqual(last_activity.description, 'Updated from "ADM" to "VOT"')
            self.assertEqual(last_activity.actor, self.user)

    def test_post_with_ids_and_all(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, all_ids=True, confirm=False, status='closed', comment='a comment', assigned_section='ADM')
        content = str(response.content)
        self.assertTrue('2 records have been updated: status set to closed' in content)
        self.assertEqual(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEqual(last_activity.verb, "Status:")
            self.assertEqual(last_activity.description, 'Updated from "new" to "closed"')
            self.assertEqual(last_activity.actor, self.user)

    def test_close_posts(self):
        ids = [report.id for report in self.reports[3:5]]
        response = self.post(ids, assigned_to=self.user.id, comment='a comment', assigned_section='ADM', status='new')
        response = self.post(ids, confirm=False, status='closed', comment='Close Posts')
        content = str(response.content)
        self.assertTrue('2 records have been updated: status set to closed' in content)
        self.assertEqual(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            first_activity = list(report.target_actions.all())[0]
            self.assertEqual(first_activity.verb, "Report closed and Assignee removed")
            self.assertTrue('Date closed updated to' in first_activity.description)
            self.assertEqual(first_activity.actor, self.user)
            self.assertEqual(report.assigned_to, None)
            self.assertEqual(report.status, "closed")

    def test_close_mixed_status_posts(self):
        first_report = Report.objects.get(id=self.reports[0].id)
        second_report = Report.objects.get(id=self.reports[1].id)
        self.post([first_report.id], confirm=False, status='closed', comment='Close Report')
        self.post([first_report.id, second_report.id], assigned_to=self.user.id, comment='a comment')
        first_report_actions = str(first_report.target_actions.all())
        second_report_actions = str(second_report.target_actions.all())
        self.assertTrue('Report closed and Assignee removed' in first_report_actions)
        self.assertTrue('Report closed and Assignee removed' not in second_report_actions)
        # This following will only effect second_report, because first_report is already closed.
        self.post([first_report.id, second_report.id], confirm=False, status='closed', comment='Close Reports with Mixed Statuses')
        first_report_actions = str(first_report.target_actions.all())
        second_report_actions = str(second_report.target_actions.all())
        self.assertTrue('Report closed and Assignee removed' in first_report_actions)
        self.assertTrue('Report closed and Assignee removed' in second_report_actions)
        first_report = Report.objects.get(id=self.reports[0].id)
        second_report = Report.objects.get(id=self.reports[1].id)
        self.assertEqual(first_report.assigned_to, self.user)
        self.assertEqual(second_report.assigned_to, None)

    def test_post_with_all(self):
        ids = [report.id for report in self.reports]
        response = self.post(ids, all_ids=True, confirm=True, summary='summary', comment='a comment', assigned_section='ADM', status='new')
        content = str(response.content)
        self.assertTrue('16 records have been updated: summary updated' in content)
        self.assertEqual(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEqual(last_activity.verb, "Added comment: ")
            self.assertEqual(last_activity.description, 'a comment')
            self.assertEqual(last_activity.actor, self.user)

    def test_post_with_email_count_sort(self):
        ids = [report.id for report in self.reports]
        self.post(ids, all_ids=True, confirm=True, return_url_args='sort=-email_count', comment='email count sort', status='closed')
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEqual(last_activity.verb, 'Status:')
            self.assertEqual(last_activity.description, 'Updated from "new" to "closed"')
            self.assertEqual(last_activity.actor, self.user)


class BulkActionsFormTests(TestCase):
    def test_bulk_actions_initial_empty(self):
        queryset = Report.objects.all()
        result = list(BulkActionsForm.get_initial_values(queryset, []))
        self.assertEqual(result, [])

    def test_bulk_actions_initial(self):
        [Report.objects.create(**SAMPLE_REPORT) for _ in range(4)]
        queryset = Report.objects.all()
        keys = ['assigned_section', 'status', 'id']
        result = list(BulkActionsForm.get_initial_values(queryset, keys))
        self.assertEqual(result, [('assigned_section', 'ADM'), ('status', 'new')])

    def test_bulk_actions_change_section(self):
        # changing the section resets primary_status, assigned_to, and status
        # the activity stream (get_action) should only report fields that actually change as a result
        Report.objects.create(**SAMPLE_REPORT)
        queryset = Report.objects.all()
        form = BulkActionsForm(queryset, {
            'assigned_section': 'APP',
            'comment': 'this is a comment'
        })
        self.assertTrue(form.is_valid())

        updates = form.get_updates()
        self.assertEqual(updates['assigned_section'], 'APP')
        self.assertEqual(updates['primary_statute'], '')
        self.assertEqual(updates['assigned_to'], '')
        self.assertEqual(updates['status'], 'new')

        # the only action in the activity stream should be the section change
        expected_actions = [
            ('Assigned section:', 'Updated from "ADM" to "APP"')
        ]
        for action in form.get_actions(queryset.first()):
            self.assertTrue(action in expected_actions)

    def test_bulk_actions_change_section_resets_user(self):
        # changing the section resets primary_status, assigned_to, and status
        # the activity stream (get_action) should only report fields that actually change as a result
        user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', secrets.token_hex(32))
        report = Report.objects.create(**SAMPLE_REPORT)
        report.assigned_to = user
        report.save()

        queryset = Report.objects.all()
        form = BulkActionsForm(queryset, {
            'assigned_section': 'APP',
            'comment': 'this is a comment'
        })
        self.assertTrue(form.is_valid())

        updates = form.get_updates()
        self.assertEqual(updates['assigned_section'], 'APP')
        self.assertEqual(updates['primary_statute'], '')
        self.assertEqual(updates['assigned_to'], '')
        self.assertEqual(updates['status'], 'new')

        # actions should include the section and assigned_to
        expected_actions = [
            ('Assigned to:', f'Updated from "{user.username}" to ""'),
            ('Assigned section:', 'Updated from "ADM" to "APP"')
        ]
        for action in form.get_actions(queryset.first()):
            self.assertTrue(action in expected_actions)


class FiltersFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

        self.email1 = 'email1@usa.gov'
        self.email2 = 'email2@usa.gov'
        ReportFactory.create_batch(3, contact_email=self.email1)
        ReportFactory.create_batch(5, contact_email=self.email2)
        ReportFactory.create_batch(8, contact_email=None)
        EmailReportCount.refresh_view()

    def test_basic_navigation(self):
        response = self.client.get(reverse('crt_forms:crt-forms-index'), {})
        self.assertEqual(response.status_code, 200)

        for row in response.context['data_dict']:
            if row['report'].contact_email == self.email1:
                self.assertEqual(row['report'].email_count, 3)
            elif row['report'].contact_email == self.email2:
                self.assertEqual(row['report'].email_count, 5)
            elif row['report'].contact_email is None:
                self.assertEqual(row['report'].email_count, None)

    def test_email_report_count_sorting_desc(self):
        query_kwargs = {'sort': '-email_count'}
        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?{urlencode(query_kwargs)}'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for index, row in enumerate(response.context['data_dict']):
            if index < 5:
                self.assertEqual(row['report'].email_count, 5)
            elif index < 8:
                self.assertEqual(row['report'].email_count, 3)
            else:
                self.assertEqual(row['report'].email_count, None)

    def test_email_report_count_sorting_asc(self):
        query_kwargs = {'sort': 'email_count'}
        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?{urlencode(query_kwargs)}'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for index, row in enumerate(response.context['data_dict']):
            if index < 3:
                self.assertEqual(row['report'].email_count, 3)
            elif index < 8:
                self.assertEqual(row['report'].email_count, 5)
            else:
                self.assertEqual(row['report'].email_count, None)

    def test_basic_multi_sort(self):
        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?sort=assigned_section&sort=contact_last_name'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for index, row in enumerate(response.context['data_dict']):
            if index == 0:
                continue

            prev_row = response.context['data_dict'][index - 1]

            if prev_row['report'].assigned_section == row['report'].assigned_section:
                self.assertTrue(prev_row['report'].contact_last_name <= row['report'].contact_last_name)
            else:
                self.assertTrue(prev_row['report'].assigned_section <= row['report'].assigned_section)

    def test_multi_sort_multi_direction(self):
        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?sort=assigned_section&sort=-contact_last_name'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for index, row in enumerate(response.context['data_dict']):
            if index == 0:
                continue

            prev_row = response.context['data_dict'][index - 1]

            if prev_row['report'].assigned_section == row['report'].assigned_section:
                self.assertTrue(prev_row['report'].contact_last_name >= row['report'].contact_last_name)
            else:
                self.assertTrue(prev_row['report'].assigned_section <= row['report'].assigned_section)

    def test_email_count_caseinsensitive(self):

        # added for case insensitive email count test
        self.email4 = 'TEST@usa.gov'
        self.email5 = 'test@usa.gov'
        self.email6 = 'TesT@usa.gov'
        self.email7 = 'tESt@usa.gov'
        # total report count should be 15 for case insensitive
        ReportFactory.create_batch(4, contact_email=self.email4)
        ReportFactory.create_batch(5, contact_email=self.email5)
        ReportFactory.create_batch(2, contact_email=self.email6)
        ReportFactory.create_batch(4, contact_email=self.email7)
        EmailReportCount.refresh_view()
        response = self.client.get(reverse('crt_forms:crt-forms-index'), {})
        self.assertEqual(response.status_code, 200)

        for row in response.context['data_dict']:

            if row['report'].contact_email in [self.email4, self.email5, self.email6, self.email7]:
                self.assertEqual(row['report'].email_count, 15)

    def test_secondary_review_filter(self):
        ReportFactory.create_batch(5, referred=True)

        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?referred=True'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for row in response.context['data_dict']:
            self.assertTrue(row['report'].referred)

    def test_assigned_report_filter(self):
        ReportFactory.create_batch(3, assigned_to=self.user)

        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?assigned_to=DELETE_USER'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['data_dict']), 3)

        for row in response.context['data_dict']:
            self.assertEqual(row['report'].assigned_to, self.user)

    def test_unassigned_report_filter(self):
        base_url = reverse('crt_forms:crt-forms-index')
        url = f'{base_url}?assigned_to=(none)'

        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)

        for row in response.context['data_dict']:
            self.assertEqual(row['report'].assigned_to, None)


class SimpleFilterFormTests(TestCase):

    def test_get_sections_returns_only_valid_choices(self):
        """
        Discard assigned_section values received in requests that are not form field choices
        """
        data = QueryDict('assigned_section=ADM&assigned_section=<script>alert()</script>')
        form = Filters(data)
        self.assertEqual({'ADM'}, form.get_section_filters)
