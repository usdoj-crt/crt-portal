"""
These are the forms that appear on the individual report page to update a report.
See test_intake_forms.py for tests of the general form and the pro form.
"""
from gettext import translation
import secrets
import urllib.parse

from unittest import mock
from botocore.docs.method import types

from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.http import QueryDict
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import urlencode

from datetime import datetime
from cts_forms.mail import render_complainant_mail, render_agency_mail

from ..forms import BulkActionsForm, ComplaintActions, ComplaintOutreach, ContactEditForm, Filters, ReportEditForm
from ..model_variables import CLOSED_STATUS, PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, NEW_STATUS
from ..models import CommentAndSummary, NotificationPreference, ReferralContact, Report, ReportDispositionBatch, ResponseTemplate, EmailReportCount, RetentionSchedule, SavedSearch
from .factories import ReportFactory, UserFactory
from .test_data import SAMPLE_REFERRAL_CONTACT, SAMPLE_REPORT_1, SAMPLE_RESPONSE_TEMPLATE


class ActionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_pass = secrets.token_hex(32)
        cls.user1 = UserFactory.create_user('USER_1', 'user1@example.com', cls.test_pass)
        cls.user2 = UserFactory.create_user('USER_2', 'user2@example.com', cls.test_pass)
        cls.schedule1 = RetentionSchedule.objects.get(name='1 Year')
        cls.schedule3 = RetentionSchedule.objects.get(name='3 Year')

    def setUp(self):
        self.initial_values = {
            'assigned_section': 'ADM',
            'status': 'new',
            'primary_statute': '144',
            'district': '1',
            'dj_number_0': '39',
            'dj_number_1': '1',
            'dj_number_2': '1234',
            'dj_number': '39-1-1234',
            'assigned_to': self.user1.pk,
            'litigation_hold': False,
        }

    def test_valid(self):
        self.initial_values.pop('assigned_to')
        form = ComplaintActions(data=self.initial_values)
        self.assertEqual(form.errors, {})

    def test_user_assignment(self):
        form = ComplaintActions(
            initial=self.initial_values,
            data={**self.initial_values, 'assigned_to': self.user2.pk},
        )

        self.assertEqual(form.errors, {})

        self.assertCountEqual(form.get_actions(), [(
            'Assigned to:',
            f'Updated from "{self.user1.username}" to "{self.user2.username}"'
        )])

    def test_user_new_assignment(self):
        form = ComplaintActions(
            initial={**self.initial_values, 'assigned_to': None},
            data={**self.initial_values, 'assigned_to': self.user2.pk},
        )

        self.assertEqual(form.errors, {})
        self.assertCountEqual(form.get_actions(), [(
            'Assigned to:',
            f'Updated from "None" to "{self.user2.username}"',
        )])

    def test_section_change(self):
        """Changes to section are recorded in activity log"""
        form = ComplaintActions(
            initial=self.initial_values,
            data={**self.initial_values, 'assigned_section': 'VOT'}
        )

        self.assertEqual(form.errors, {})
        self.assertCountEqual(form.get_actions(), [
            ('Assigned section:', 'Updated from "ADM" to "VOT"')
        ])

    def test_dj_number(self):
        form = ComplaintActions(
            initial=self.initial_values,
            data={
                **self.initial_values,
                'dj_number_0': '170',
                'dj_number_1': '12C',
                'dj_number_2': '1234',
            }
        )

        self.assertEqual(form.errors, {})

        self.assertCountEqual(form.get_actions(), [
            ('ICM DJ Number:', 'Updated from "39-1-1234" to "170-12C-1234"'),
        ])

    def test_retention_schedule(self):
        self.initial_values['retention_schedule'] = self.schedule1.pk
        privileged_user = mock.MagicMock()
        privileged_user.has_perm.return_value = True
        form = ComplaintActions(
            initial=self.initial_values,
            data={
                **self.initial_values,
                'retention_schedule': self.schedule3.pk,
            },
            user=privileged_user
        )

        self.assertEqual(form.errors, {})

        self.assertCountEqual(form.get_actions(), [
            ('Retention schedule:', 'Updated from "1 Year" to "3 Year"'),
        ])

    def test_retention_schedule_without_permissions(self):
        self.initial_values['retention_schedule'] = self.schedule1.pk
        unprivileged_user = mock.MagicMock()
        unprivileged_user.has_perm.return_value = False
        form = ComplaintActions(
            initial=self.initial_values,
            data={
                **self.initial_values,
                'retention_schedule': self.schedule3.pk,
            },
            user=unprivileged_user
        )

        # There should not be errors because field should be disabled and the new value ignored
        self.assertDictEqual(form.errors, {})

        self.assertCountEqual(form.get_actions(), [])

    def test_bulk_retention_schedule(self):
        privileged_user = mock.MagicMock()
        privileged_user.has_perm.return_value = True
        a = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', retention_schedule=self.schedule3)
        b = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', retention_schedule=self.schedule1)
        queryset = Report.objects.all().filter(pk__in=[a.pk, b.pk])

        form = BulkActionsForm(queryset, {
            'retention_schedule': self.schedule3.pk,
            'comment': 'Test bulk change',
        }, user=privileged_user)
        form.full_clean()

        self.assertEqual(form.errors, {})
        self.assertCountEqual(form.get_actions(a), [
        ])
        self.assertCountEqual(form.get_actions(b), [
            ('Retention schedule:', 'Updated from "1 Year" to "3 Year"'),
        ])

    def test_bulk_retention_schedule_without_permissions(self):
        self.initial_values['retention_schedule'] = self.schedule1.pk
        unprivileged_user = mock.MagicMock()
        unprivileged_user.has_perm.return_value = False
        a = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', retention_schedule=self.schedule1, litigation_hold=False)
        b = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', retention_schedule=self.schedule1, litigation_hold=False)
        queryset = Report.objects.all().filter(pk__in=[a.pk, b.pk])

        form = BulkActionsForm(queryset, {
            'assigned_section': SAMPLE_REPORT_1['assigned_section'],
            'status': NEW_STATUS,
            'retention_schedule': self.schedule3.pk,
            'litigation_hold': '',
            'comment': 'Test bulk change',
        }, user=unprivileged_user)
        form.full_clean()

        # The behavior is to ignore changes (because the field is disabled, so users shouldn't be able to make changes).
        # So, we're just asserting there's no retention_schedule change here:
        self.assertCountEqual(form.get_actions(a), [])
        self.assertCountEqual(form.get_actions(b), [])

    def test_unviewed_reports_raises_error(self):
        unviewed = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', retention_schedule=self.schedule1, viewed=False)
        viewed = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', retention_schedule=self.schedule1, viewed=True)
        queryset = Report.objects.all().filter(pk__in=[viewed.pk, unviewed.pk])

        form = BulkActionsForm(queryset, {
            'status': CLOSED_STATUS,
            'comment': 'Test bulk change',
        })
        form.full_clean()

        self.assertDictEqual(form.errors, {
            '__all__': [
                'Not all reports in the queryset have been viewed. Each report must be viewed before it can be closed.'
            ],
        })

    def test_litigation_hold_turns_on(self):
        instance = Report.objects.create(**SAMPLE_REPORT_1,
                                         public_id='foo',
                                         litigation_hold=False)
        form = ComplaintActions(
            instance=instance,
            initial=self.initial_values,
            data={
                **self.initial_values,
                'litigation_hold': True,
            }
        )

        self.assertEqual(form.errors, {})

        self.assertCountEqual(form.get_actions(), [
            ('Litigation hold:', 'Updated from "False" to "True"'),
        ])

    def test_litigation_hold_blocks_single_edits(self):
        instance = Report.objects.create(**SAMPLE_REPORT_1, litigation_hold=True)
        form = ComplaintActions(
            instance=instance,
            initial={
                **self.initial_values,
                'litigation_hold': True,
            },
            data={
                **self.initial_values,
                'litigation_hold': True,
                'assigned_section': 'APP',
            }
        )

        self.assertIn(
            form.errors.get('__all__', ['Error not present'])[0],
            f'No changes can be made to report {instance.public_id} while it is under litigation hold'
        )

    def test_litigation_hold_blocks_for_all_forms(self):
        instance = Report.objects.create(**SAMPLE_REPORT_1,
                                         public_id='foo',
                                         litigation_hold=True)
        forms_and_changes = [
            (ComplaintActions, {'assigned_section': 'APP'}),
            (ComplaintOutreach, {'origination_utm_content': 'foo'}),
            (ContactEditForm, {'contact_first_name': 'foo'}),
            (ReportEditForm, {'primary_complaint': 'workplace'}),
        ]

        errors = []
        for factory, changes in forms_and_changes:
            factory = factory(
                instance=instance,
                initial=self.initial_values,
                data={
                    **self.initial_values,
                    **changes,
                }
            )
            factory.instance.public_id = 'foo'
            if factory.errors:
                errors.append((factory.__class__.__name__, factory.errors))

        self.assertEqual(errors, [])

    def test_litigation_hold_off_allows_edits(self):
        hold_off_and_unchanged = ComplaintActions(
            initial={
                **self.initial_values,
                'litigation_hold': False,
            },
            data={
                **self.initial_values,
                'assigned_section': 'APP',
            }
        )
        hold_on_and_changed = ComplaintActions(
            initial={
                **self.initial_values,
                'litigation_hold': False,
            },
            data={
                **self.initial_values,
                'assigned_section': 'APP',
                'litigation_hold': True,
            }
        )

        self.assertEqual(hold_off_and_unchanged.errors, {})
        self.assertEqual(hold_on_and_changed.errors, {})

    def test_litigation_hold_blocks_bulk_edits(self):
        a = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', litigation_hold=True)
        b = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', litigation_hold=True)
        c = Report.objects.create(**SAMPLE_REPORT_1, public_id='c')

        queryset = Report.objects.all().filter(pk__in=[a.pk, b.pk, c.pk])
        form = BulkActionsForm(queryset, {
            'assigned_section': 'APP',
            'comment': 'Test bulk change',
        })
        form.full_clean()

        self.assertIn(
            form.errors.get('__all__', ['Error not present'])[0],
            'No changes can be made to reports a, b while they are under litigation hold'
        )

    def test_litigation_hold_allows_bulk_disabling(self):
        a = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', litigation_hold=True)
        b = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', litigation_hold=True)
        c = Report.objects.create(**SAMPLE_REPORT_1, public_id='c')
        privileged_user = mock.MagicMock()
        privileged_user.has_perm.return_value = True

        queryset = Report.objects.all().filter(pk__in=[a.pk, b.pk, c.pk])
        form = BulkActionsForm(queryset, {
            'assigned_section': 'APP',
            'litigation_hold': 'off',
            'comment': 'Test bulk change',
        }, user=privileged_user)
        form.full_clean()

        self.assertCountEqual(form.get_actions(a), [
            ('Litigation hold:', 'Updated from "True" to "False"'),
            ('Assigned section:', 'Updated from "ADM" to "APP"'),
        ])
        self.assertCountEqual(form.get_actions(b), [
            ('Litigation hold:', 'Updated from "True" to "False"'),
            ('Assigned section:', 'Updated from "ADM" to "APP"'),
        ])
        self.assertCountEqual(form.get_actions(c), [
            ('Assigned section:', 'Updated from "ADM" to "APP"'),
        ])
        self.assertEqual(form.errors, {})

    def test_litigation_hold_allows_bulk_enabling(self):
        a = Report.objects.create(**SAMPLE_REPORT_1, public_id='a', litigation_hold=True)
        b = Report.objects.create(**SAMPLE_REPORT_1, public_id='b', litigation_hold=True)
        c = Report.objects.create(**SAMPLE_REPORT_1, public_id='c')

        queryset = Report.objects.all().filter(pk__in=[a.pk, b.pk, c.pk])
        form = BulkActionsForm(queryset, {
            'assigned_section': SAMPLE_REPORT_1['assigned_section'],
            'status': NEW_STATUS,
            'litigation_hold': 'on',
            'comment': 'Test bulk change',
        })
        form.full_clean()

        self.assertCountEqual(form.get_actions(a), [])
        self.assertCountEqual(form.get_actions(b), [])
        self.assertCountEqual(form.get_actions(c), [
            ('Litigation hold:', 'Updated from "False" to "True"'),
        ])
        self.assertEqual(form.errors, {})

    def test_referral(self):
        form = ComplaintActions(
            initial={
                **self.initial_values,
                'assigned_to': None,
                'referred': False,
            },
            data={
                **self.initial_values,
                'assigned_to': None,
                'referred': True,
            }
        )
        self.assertEqual(form.errors, {})
        self.assertCountEqual(form.get_actions(), [
            ('Secondary review:', 'Updated from "False" to "True"'),
        ])


class NotificationPreferencesTests(TestCase):
    unsubscribe = reverse('crt_forms:crt-forms-notifications-unsubscribe')

    def setUp(self):
        self.client = Client()
        self.users = types.SimpleNamespace(
            subscribed=UserFactory.create_user('SUBSCRIBED_USER', 'subscribed@example.com', 'password'),
            unsubscribed=UserFactory.create_user('UNSUBSCRIBED_USER', 'unsubscribed@example.com', 'password'),
            noprefs=UserFactory.create_user('NOPREFS_USER', 'noprefs@example.com', 'password'),
        )
        NotificationPreference.objects.create(
            user=self.users.subscribed,
            assigned_to='individual',
        )
        NotificationPreference.objects.create(
            user=self.users.unsubscribed,
            assigned_to='none',
        )

    def test_unsubscribe_unsubscribes(self):
        """The comment shows up in the report's activity log"""
        user = self.users.subscribed
        self.client.login(username=user.username,
                          password='password')

        response = self.client.get(self.unsubscribe)

        self.assertRedirects(response,
                             '/form/notifications/',
                             fetch_redirect_response=True)
        self.assertIn('You have been unsubscribed from all portal notifications',
                      [m.message for m in get_messages(response.wsgi_request)])
        user.refresh_from_db()
        self.assertFalse(hasattr(user, 'notification_preference'))

    def test_unsubscribe_safe_for_no_prefs(self):
        """The comment shows up in the report's activity log"""
        user = self.users.noprefs
        self.client.login(username=user.username,
                          password='password')

        response = self.client.get(self.unsubscribe)

        self.assertRedirects(response,
                             '/form/notifications/',
                             fetch_redirect_response=True)
        self.assertIn('You are not subscribed to notifications',
                      [m.message for m in get_messages(response.wsgi_request)])
        user.refresh_from_db()
        self.assertFalse(hasattr(user, 'notification_preference'))

    def test_unsubscribe_safe_for_not_subscribed(self):
        """The comment shows up in the report's activity log"""
        user = self.users.unsubscribed
        self.client.login(username=user.username,
                          password='password')

        response = self.client.get(self.unsubscribe)

        self.assertRedirects(response,
                             '/form/notifications/',
                             fetch_redirect_response=True)
        self.assertIn('You have been unsubscribed from all portal notifications',
                      [m.message for m in get_messages(response.wsgi_request)])
        user.refresh_from_db()
        self.assertFalse(hasattr(user, 'notification_preference'))


class CommentActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
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
        self.report_data = SAMPLE_REPORT_1.copy()
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
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
        self.template = ResponseTemplate.objects.create(**SAMPLE_RESPONSE_TEMPLATE)

    def post_template_action(self, what, **form_kwargs):
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'templates_default': self.template.id,
                'selected_tab': 'response-template-default',
                'type': what,
                'next': '?per_page=15',
                **form_kwargs,
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
        response = self.client.get(
            reverse(
                'api:response-detail',
                kwargs={'pk': 1},
            ) + f"?report_id={self.report.id}"
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
        response = self.client.get(
            reverse(
                'api:response-detail',
                kwargs={'pk': 1},
            ) + f"?report_id={self.report.id}"
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 31, 2020' in content)
        self.assertFalse('You contacted the Department of Justice on December 1, 2000' in content)

    def test_bad_crt_receipt_date(self):
        # Ignore crt_reciept_date it is not valid
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.crt_reciept_day = None
        self.report.intake_format = 'fax'
        self.report.save()
        response = self.client.get(
            reverse(
                'api:response-detail',
                kwargs={'pk': 1},
            ) + f"?report_id={self.report.id}"
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 31, 2020' in content)
        self.assertFalse('You contacted the Department of Justice on December 1, 2000' in content)

    def test_crt_receipt_date(self):
        # use crt_reciept_date
        self.report.create_date = datetime(2020, 12, 31, 23, 0, 0)
        self.report.intake_format = 'fax'
        self.report.save()
        response = self.client.get(
            reverse(
                'api:response-detail',
                kwargs={'pk': 1},
            ) + f"?report_id={self.report.id}"
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('You contacted the Department of Justice on December 1, 2000' in content)
        self.assertFalse('You contacted the Department of Justice on December 31, 2020' in content)


class FormNavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
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

    def test_view_all_descriptions(self):
        first = self.reports[-1]
        first.violation_summary = 'this is my summary'
        first.save()

        response = self.client.get(
            reverse('crt_forms:crt-forms-show', args=[first.id])
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        expected = ('/form/view/'
                    '?violation_summary=^this%20is%20my%20summary$'
                    '&amp;assigned_section=ADM')
        self.assertIn(expected, content)

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
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
        Report.objects.create(**SAMPLE_REPORT_1)

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
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT_1)

    def test_secondary_review_checked(self):
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        params = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            'referred': 'on',
            'assigned_section': 'ADM',
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Secondary review:' in content)
        self.assertTrue(escape('Updated from "False" to "True"') in content)
        self.report.refresh_from_db()
        self.assertTrue(self.report.referred)

    def test_secondary_review_unchecked(self):
        self.report.referred = True
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

    def test_change_section(self):
        # After the second post, when the report is reassigned to a new section, the primary_statute
        # should be reset
        params_1 = {
            'type': 'actions',
            # Keep the same status as when the report was created.
            'status': NEW_STATUS,
            'assigned_to': '',
            'assigned_section': 'ADM',
            'primary_statute': '144',
            'dj_number_0': '39',
            'dj_number_1': '1',
            'dj_number_2': '1234',
        }
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})
        response = self.client.post(url, params_1, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.report.primary_statute, '144')
        params_2 = {
            'type': 'actions',
            'status': NEW_STATUS,
            'assigned_to': '',
            'assigned_section': 'HCE',
            'dj_number_0': '39',
            'dj_number_1': '1',
            'dj_number_2': '1234',
        }
        response = self.client.post(url, params_2, follow=True)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        first_activity = list(self.report.target_actions.all())[0]
        second_activity = list(self.report.target_actions.all())[1]
        self.assertEqual('Updated from "144" to ""', first_activity.description)
        self.assertEqual('Updated from "ADM" to "HCE"', second_activity.description)
        self.assertEqual(self.report.primary_statute, None)


class BulkActionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.reports = ReportFactory.create_batch(16, assigned_section='ADM', status='new', viewed=True)

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
            'action': 'print',
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
        self.assertTrue(escape("2 records have been updated: section set to VOT, status set to new, assigned to '', primary classification set to '', retention schedule set to '', secondary review set to '', and dj number set to ''") in content)
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
        form = BulkActionsForm(queryset)
        result = list(form.get_initial_values(queryset, []))
        self.assertEqual(result, [])

    def test_bulk_actions_initial(self):
        [Report.objects.create(**SAMPLE_REPORT_1) for _ in range(4)]
        queryset = Report.objects.all()
        keys = ['assigned_section', 'status', 'id']
        form = BulkActionsForm(queryset)
        result = list(form.get_initial_values(queryset, keys))
        self.assertEqual(result, [('assigned_section', 'ADM'), ('status', 'new')])

    def test_bulk_actions_change_section(self):
        # changing the section resets primary_status, assigned_to, and status
        # the activity stream (get_action) should only report fields that actually change as a result
        Report.objects.create(**SAMPLE_REPORT_1)
        queryset = Report.objects.all()
        form = BulkActionsForm(queryset, {
            'assigned_section': 'APP',
            'comment': 'this is a comment'
        })
        self.assertTrue(form.is_valid())

        updates = form.get_updates()
        self.assertEqual(updates['assigned_section'], 'APP')
        self.assertEqual(updates['primary_statute'], None)
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
        user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', secrets.token_hex(32))
        report = Report.objects.create(**SAMPLE_REPORT_1)
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
        self.assertEqual(updates['primary_statute'], None)
        self.assertEqual(updates['assigned_to'], '')
        self.assertEqual(updates['status'], 'new')

        # actions should include the section and assigned_to
        expected_actions = [
            ('Assigned to:', f'Updated from "{user.username}" to ""'),
            ('Assigned section:', 'Updated from "ADM" to "APP"')
        ]
        for action in form.get_actions(queryset.first()):
            self.assertTrue(action in expected_actions)


class BulkDispositionFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass, first_name='Ringo', last_name='Starr')
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.batch = ReportDispositionBatch()

    def test_create_batch(self):
        [Report.objects.create(**SAMPLE_REPORT_1) for _ in range(4)]
        queryset = Report.objects.all()
        ids = [report.id for report in queryset]
        url = reverse('crt_forms:disposition-actions')
        params = {
            'uuid': self.batch.uuid,
            'proposed_disposal_date': datetime(datetime.today().year + 1, 1, 1),
            'create_date': datetime.today().strftime('%m/%d/%Y'),
            'disposed_count': 4,
            'disposed_by': 'Ringo Starr',
            'ids': ids,
            'id': '',
        }
        try:
            with translation.atomic():
                response = self.client.post(url, params, follow=True)
                content = str(response.content)
                self.assertEqual(response.status_code, 200)
                self.assertTrue('4 records have been approved for disposal' in content)
        except Exception:
            pass


class BatchActionFormTests(TestCase):
    def setUp(self):
        self.test_pass = secrets.token_hex(32)
        user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass, first_name='Ringo', last_name='Starr')
        schedule = RetentionSchedule.objects.get(name='1 Year')
        [Report.objects.create(**SAMPLE_REPORT_1, retention_schedule=schedule, viewed=True) for _ in range(4)]
        queryset = Report.objects.all()
        self.batch = ReportDispositionBatch.objects.create(
            proposed_disposal_date=datetime(datetime.today().year + 1, 1, 1),
            create_date=datetime.today(),
            disposed_count=4,
            disposed_by=user
        )
        self.batch.add_records_to_batch(queryset, user)
        self.user_reviewer = UserFactory.create_user('REVIEWER', 'paul@thebeatles.com', self.test_pass, first_name='Paul', last_name='McCartney')
        group = Group.objects.get(name='Records Team')
        group.user_set.add(self.user_reviewer)
        self.second_user_reviewer = UserFactory.create_user('SECOND_REVIEWER', 'john@thebeatles.com', self.test_pass, first_name='John', last_name='Lennon')
        group.user_set.add(self.second_user_reviewer)

    def test_approve_batch(self):
        client = Client()
        client.login(username='REVIEWER', password=self.test_pass)
        url = reverse('crt_forms:disposition-batch-actions', kwargs={'id': self.batch.uuid})
        params = {
            'status': 'verified',
            'first_review_date': datetime.today().strftime('%m/%d/%Y'),
            'first_reviewer': self.user_reviewer.pk,
        }
        response = client.post(url, params, follow=True)
        content = str(response.content)
        self.assertIn('has been verified for disposal', content)

        client.login(username='SECOND_REVIEWER', password=self.test_pass)
        params = {
            'status': 'approved',
            'second_review_date': datetime.today().strftime('%m/%d/%Y'),
            'second_reviewer': self.second_user_reviewer.pk,
        }
        response = client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('has been approved for disposal', content)

    def test_reject_batch(self):
        client = Client()
        client.login(username='SECOND_REVIEWER', password=self.test_pass)
        url = reverse('crt_forms:disposition-batch-actions', kwargs={'id': self.batch.uuid})
        params = {
            'status': 'rejected',
            'first_review_date': datetime.today().strftime('%m/%d/%Y'),
            'first_reviewer': self.user_reviewer.pk,
            'second_reviewer': self.second_user_reviewer.pk,
            'second_review_date': datetime.today().strftime('%m/%d/%Y'),
        }
        response = client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('has been rejected for disposal' in content)


class FiltersFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
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


class ReferralEmailContentTests(TestCase):

    def setUp(self):
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
        self.referral_contact = ReferralContact.objects.create(**SAMPLE_REFERRAL_CONTACT)
        self.template = ResponseTemplate.objects.create(
            **SAMPLE_RESPONSE_TEMPLATE,
            referral_contact=self.referral_contact,
        )

    @override_settings(RESTRICT_EMAIL_RECIPIENTS_TO=['a@example.gov', 'b@example.gov'])
    def test_build_referral_content(self):
        complainant_letter = render_complainant_mail(report=self.report, template=self.template, action='email')

        referral_letter = render_agency_mail(complainant_letter=complainant_letter,
                                             template=self.template,
                                             report=self.report)

        self.assertIsNotNone(referral_letter)

        self.assertEqual(referral_letter.recipients, ['a@example.gov', 'b@example.gov'])
        self.assertEqual(referral_letter.subject, f'[DOJ CRT Referral] {self.report.public_id} - Lincoln Abraham')
        self.assertIn(f'<strong>Subject:</strong> test data with record {self.report.public_id}', referral_letter.html_message)
        self.assertIn('<strong>First name:</strong> Lincoln', referral_letter.html_message)


class SavedSearchActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.saved_search = SavedSearch.objects.create(
            name='APP Saved Search',
            query='location_state=AK&intake_format=web&grouping=default',
            section='ADM'
        )

    def test_update_search(self):
        url = reverse('crt_forms:saved-search-actions', kwargs={'id': self.saved_search.id})
        params = {
            'section_filter': '&section_filter=APP',
            'name': 'APP Saved Search',
            'query': 'location_state=AK&intake_format=web&grouping=default',
            'section': 'APP'
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Successfully updated Section' in content)
        self.saved_search.refresh_from_db()
        self.assertTrue(self.saved_search.section == 'APP')

    def test_create_search(self):
        url = reverse('crt_forms:saved-search-actions')
        params = {
            'section_filter': 'ADM',
            'section': 'ADM',
            'name': 'ADM Search',
            'query': 'location_state=IL&commercial_or_public_place=place_of_worship'
        }
        response = self.client.post(url, params, follow=True)
        content = str(response.content)
        self.assertTrue('Successfully added new saved search' in content)
