"""Back end forms"""
import secrets
import urllib.parse

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils.html import escape

from ..forms import ComplaintActions, ReportEditForm
from ..model_variables import PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES
from ..models import CommentAndSummary, Report, ResponseTemplate
from .test_data import SAMPLE_REPORT, SAMPLE_RESPONSE_TEMPLATE
from .test_data import SAMPLE_REPORT, SAMPLE_RESPONSE_TEMPLATE, SAMPLE_COMPLAINT


class ActionTests(TestCase):
    def test_valid(self):
        form = ComplaintActions(data={
            'assigned_section': 'ADM',
            'status': 'new',
            'primary_statute': '144',
            'district': '1',
        })
        self.assertTrue(form.is_valid())


class CommentActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

        self.note = 'Important note'
        self.report = Report.objects.create(**SAMPLE_REPORT)
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
        self.assertEquals(self.response.status_code, 200)

    def test_retain_query(self):
        """if the user came to the page with query parameters, keep them for the back to all button."""
        self.assertTrue('?per_page=15' in str(self.response.content))

    def test_creates_comment(self):
        """A comment is created and associated with the right report"""
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        report = Report.objects.filter(internal_comments__pk=comment_id)[0]
        self.assertEquals(report.pk, self.pk)

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
        self.assertEquals(response.status_code, 200)

class ComplaintActionsTests(TestCase):    
    def setUp(self):
        self.complaint_data = SAMPLE_COMPLAINT.copy()
        self.complaint = Report.objects.create(**self.complaint_data)
    
    def test_changed_data_assigned_section(self):
        data = self.complaint_data.copy()
        data.update({'assigned_section': 'APP'})
        form = ComplaintActions(data, instance=self.complaint)
        self.assertTrue(form.is_valid())
        self.assertTrue('assigned_section' in form.changed_data)


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
        self.assertEquals(response.status_code, 200)
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
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('?per_page=15' in content)
        self.assertFalse('Contacted complainant:' in content)


class FormNavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.reports = [Report.objects.create(**SAMPLE_REPORT) for _ in range(3)]
        # generate three reports that belong to a specific section
        self.filter_section = 'ADM'
        for report in self.reports:
            report.assigned_section = self.filter_section
            report.save()
        # generate random reports that belong to other sections
        reports = [Report.objects.create(**SAMPLE_REPORT) for _ in range(7)]
        sections = ['CRM', 'DRS', 'ELS', 'EOS']
        for index, report in enumerate(reports):
            report.assigned_section = sections[index % len(sections)]
            report.save()

    def test_basic_navigation(self):
        first = self.reports[-1]
        response = self.client.get(
            reverse('crt_forms:crt-forms-show', kwargs={'id': first.id}),
            {
                'next': f'?per_page=15&assigned_section={self.filter_section}',
                'index': '0',
            },
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('1 of 3 records' in content)
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[1].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url}?next={next_qp}&index=1") in content)
        self.assertEquals(content.count('complaint-nav'), 2)
        self.assertEquals(content.count('disabled-nav'), 1)

    def test_invalid_index_navigation(self):
        second = self.reports[1]
        response = self.client.get(
            reverse('crt_forms:crt-forms-show', kwargs={'id': second.id}),
            {
                'next': f'?per_page=15&assigned_section={self.filter_section}',
                'index': '5000',
            },
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('2 of 3 records' in content)
        url1 = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[2].id})
        url2 = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[0].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url1}?next={next_qp}&index=0") in content)
        self.assertTrue(escape(f"{url2}?next={next_qp}&index=2") in content)
        self.assertEquals(content.count('complaint-nav'), 2)
        self.assertEquals(content.count('disabled-nav'), 0)

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
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('N/A of 2 records' in content)
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.reports[0].id})
        next_qp = urllib.parse.quote('?per_page=15&assigned_section=ADM')
        self.assertTrue(escape(f"{url}?next={next_qp}&index=1") in content)
        self.assertEquals(content.count('complaint-nav'), 2)
        self.assertEquals(content.count('disabled-nav'), 1)


class PrintActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT)

    def post_print_action(self, options):
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
        self.assertEquals(response.status_code, 200)
        return str(response.content)

    def test_response_action_print(self):
        options = ['correspondent', 'activity']
        content = self.post_print_action(options)
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Printed report' in content)
        self.assertTrue(escape('Selected correspondent, activity') in content)


class BulkActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.reports = [Report.objects.create(**SAMPLE_REPORT) for _ in range(16)]

    def get(self, ids, all_ids=False):
        params = {
            'next': '?per_page=15&status=open&something=else',
            'id': ids,
        }
        if all_ids:
            params['all'] = 'all'
        response = self.client.get(reverse('crt_forms:crt-forms-actions'), params)
        self.assertEquals(response.status_code, 200)
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

    def post(self, ids, all_ids=False, confirm=False, **extra):
        params = {
            'next': '?per_page=15',
            'ids': ','.join([str(id) for id in ids]),
            **extra,
        }
        if all_ids:
            params['all'] = 'all'
        if confirm:
            params['confirm_all'] = 'confirm_all'
        response = self.client.post(reverse('crt_forms:crt-forms-actions'), params, follow=True)
        self.assertEquals(response.status_code, 200)
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
        user = User.objects.get(username='DELETE_USER')
        response = self.post(ids, assigned_to=user.id, comment='a comment')
        content = str(response.content)
        self.assertTrue('2 records have been updated: assigned to DELETE_USER' in content)
        self.assertEquals(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEquals(last_activity.verb, "Assigned to:")
            self.assertEquals(last_activity.description, 'Updated from "None" to "DELETE_USER"')
            self.assertEquals(last_activity.actor, user)

    def test_post_with_ids_and_all(self):
        ids = [report.id for report in self.reports[3:5]]
        user = User.objects.get(username='DELETE_USER')
        response = self.post(ids, all_ids=True, confirm=False, status='closed', comment='a comment')
        content = str(response.content)
        self.assertTrue('2 records have been updated: status set to closed' in content)
        self.assertEquals(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEquals(last_activity.verb, "Status:")
            self.assertEquals(last_activity.description, 'Updated from "new" to "closed"')
            self.assertEquals(last_activity.actor, user)

    def test_post_with_all(self):
        ids = [report.id for report in self.reports]
        user = User.objects.get(username='DELETE_USER')
        response = self.post(ids, all_ids=True, confirm=True, summary='summary', comment='a comment')
        content = str(response.content)
        self.assertTrue('16 records have been updated: summary updated' in content)
        self.assertEquals(response.request['PATH_INFO'], reverse('crt_forms:crt-forms-index'))
        for report_id in ids:
            report = Report.objects.get(id=report_id)
            last_activity = list(report.target_actions.all())[-1]
            self.assertEquals(last_activity.verb, "Added comment: ")
            self.assertEquals(last_activity.description, 'a comment')
            self.assertEquals(last_activity.actor, user)
