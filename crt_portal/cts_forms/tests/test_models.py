"""
Testing multilingual properties used to make messages
"""
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from types import SimpleNamespace

import datetime

from .factories import ReportFactory

from cts_forms.models import JudicialDistrict, Report, ReportDispositionBatch, RetentionSchedule, User, SavedSearch, ScheduledNotification, ProtectedClass, HateCrimesandTrafficking, Tag, ReportAttachment, CommentAndSummary, Campaign, EeocOffice

from tms.models import TMSEmail

from utils import activity
from .test_data import SAMPLE_REPORT_1


class ReportSimpleTests(SimpleTestCase):

    def test_contact_full_name_with_first_and_last(self):
        report = ReportFactory.build()
        expected = f'{report.contact_first_name} {report.contact_last_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_only_first(self):
        report = ReportFactory.build(contact_last_name="")
        expected = f'{report.contact_first_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_only_last(self):
        report = ReportFactory.build(contact_first_name="")
        expected = f'{report.contact_last_name}'
        self.assertEqual(report.contact_full_name, expected)

    def test_contact_full_name_with_none(self):
        report = ReportFactory.build(contact_first_name="", contact_last_name="")
        expected = ""
        self.assertEqual(report.contact_full_name, expected)

    def test_addressee_with_first_and_last(self):
        report = ReportFactory.build()
        expected = f"Dear {report.contact_full_name}"
        self.assertEqual(report.addressee, expected)

    def test_addressee_with_only_first(self):
        report = ReportFactory.build(contact_last_name="")
        expected = f"Dear {report.contact_full_name}"
        self.assertEqual(report.addressee, expected)

    def test_addressee_with_none(self):
        report = ReportFactory.build(contact_last_name="", contact_first_name="")
        expected = "Thank you for your report"
        self.assertEqual(report.addressee, expected)

    def test_contact_emails(self):
        report: Report = ReportFactory.build()
        report.contact_email = 'one@example.com'
        report.contact_2_email = 'two@example.com'
        report.contact_3_email = 'three@example.com'
        report.contact_4_email = 'four@example.com'
        self.assertEqual(report.contact_emails, [
            'one@example.com',
            'two@example.com',
            'three@example.com',
            'four@example.com',
        ])

    def test_missing_contact_emails(self):
        report: Report = ReportFactory.build()
        report.contact_email = 'one@example.com'
        report.contact_2_email = ''
        report.contact_3_email = ''
        report.contact_4_email = 'four@example.com'
        self.assertEqual(report.contact_emails, [
            'one@example.com',
            'four@example.com',
        ])

    def test_no_contact_emails(self):
        report: Report = ReportFactory.build()
        report.contact_email = ''
        report.contact_2_email = ''
        report.contact_3_email = ''
        report.contact_4_email = ''

        self.assertEqual(report.contact_emails, [])


class ScheduledNotificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ScheduledNotification.objects.all().delete()
        User.objects.filter(username='notification_test_user').delete()
        cls.test_user = User.objects.create(username='notification_test_user')

    def test_finds_existing_for_user(self):
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"yes"',
            frequency='weekly',
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            was_sent=False,
        )
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"no"',
            frequency='weekly',
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            was_sent=True,
        )
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"no"',
            frequency='daily',
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            was_sent=False,
        )

        scheduled = ScheduledNotification.find_for(self.test_user, 'weekly')

        self.assertEqual(scheduled.notifications, '"yes"')

    def test_creates_for_user(self):
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"no"',
            frequency='weekly',
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            was_sent=True,
        )
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"no"',
            frequency='daily',
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            was_sent=False,
        )

        scheduled = ScheduledNotification.find_for(self.test_user, 'weekly')
        self.assertEqual(scheduled.notifications, {})
        self.assertEqual(scheduled.frequency, 'weekly')
        self.assertEqual(scheduled.recipient, self.test_user)
        self.assertFalse(scheduled.was_sent)
        self.assertGreater(scheduled.scheduled_for, datetime.datetime.now())

    def test_finds_ready_to_send(self):
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            scheduled_for=datetime.datetime.now() + datetime.timedelta(days=1),
            notifications='"no"',
            was_sent=False,
        )
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"no"',
            scheduled_for=datetime.datetime.now() - datetime.timedelta(days=1),
            was_sent=True,
        )
        ScheduledNotification.objects.create(
            recipient=self.test_user,
            notifications='"yes"',
            scheduled_for=datetime.datetime.now() - datetime.timedelta(days=1),
            was_sent=False,
        )

        ready = ScheduledNotification.find_ready_to_send()

        self.assertEqual([r.notifications for r in ready], ['"yes"'])


class SavedSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SavedSearch.objects.all().delete()

    def test_sets_short_url_on_save(self):
        search = SavedSearch(name='Test !! Search', query='status=new')
        search2 = SavedSearch(name='Test !! Search', query='status=open')

        search.save()
        search2.save()

        self.assertEqual(search.shortened_url.shortname, 'search/test-search')
        self.assertEqual(search2.shortened_url.shortname, 'search/test-search-1')
        self.assertEqual(search.shortened_url.destination, '/form/view?status=new')
        self.assertEqual(search2.shortened_url.destination, '/form/view?status=open')
        self.assertTrue(search.shortened_url.enabled)
        self.assertTrue(search2.shortened_url.enabled)

    def test_changes_short_url_when_exists(self):
        search = SavedSearch(name='Initial', query='status=new')
        search.save()

        search.name = 'Changed'
        search.save()

        self.assertEqual(search.shortened_url.shortname, 'search/changed')
        self.assertEqual(search.shortened_url.destination, '/form/view?status=new')
        self.assertTrue(search.shortened_url.enabled)


class ReportTests(TestCase):
    test_user = User(username='disposition_test_user')

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user.save()
        test_data = {
            **SAMPLE_REPORT_1.copy(),
            'retention_schedule': RetentionSchedule.objects.get(name='1 Year'),
            'location_name': 'batch disposition tests',
        }
        for schedule in ['1 Year', '3 Year', '3 Year']:
            kwargs = {
                **test_data,
                'retention_schedule': RetentionSchedule.objects.get(name=schedule)
            }
            Report.objects.create(**kwargs)

    @mock.patch('crequest.middleware.CrequestMiddleware.get_request',
                return_value=mock.Mock(user=test_user))
    def test_disposition(self, mock_crequest_middleware: mock.Mock):
        reports = Report.objects.filter(location_name='batch disposition tests')
        batch = ReportDispositionBatch.dispose(reports)
        self.assertEqual(batch.disposed_by.get_username(), 'disposition_test_user')
        self.assertEqual(batch.disposed_count, 3)
        self.assertEqual(batch.disposed_reports.count(), 3)
        self.assertEqual({
            disposed.schedule.name
            for disposed in batch.disposed_reports.all()
        }, {'1 Year', '3 Year'})
        self.assertEqual({
            disposed.public_id
            for disposed in batch.disposed_reports.all()
        }, {
            original.public_id
            for original in reports.all()
        })

    class DistrictEdgeCase(SimpleNamespace):
        city_user_enters: str
        expected_correction: str

    district_edge_cases = [
        DistrictEdgeCase(city_user_enters='normal city',
                         expected_correction='NORMAL CITY'),
        DistrictEdgeCase(city_user_enters='st petersburg',
                         expected_correction='SAINT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='ft petersburg',
                         expected_correction='FORT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='st. petersburg',
                         expected_correction='SAINT PETERSBURG'),
        DistrictEdgeCase(city_user_enters='ft. petersburg',
                         expected_correction='FORT PETERSBURG'),
    ]

    def test_assign_district_edge_cases(self):
        for case in self.district_edge_cases:
            JudicialDistrict.objects.filter(city=case.expected_correction).delete()
            JudicialDistrict.objects.create(
                city=case.expected_correction, state='FL', district='123ABC')
            report = ReportFactory.build(
                location_city_town=case.city_user_enters, location_state='FL')
            district = report.assign_district()
            self.assertEqual(district, '123ABC')

    def test_report_hides_disposed(self):
        report = ReportFactory.build()
        report.save()
        report.redact()
        self.assertFalse(Report.objects.filter(pk=report.pk).exists())
        self.assertTrue(Report.all_objects.filter(pk=report.pk).exists())

    def test_report_disposes(self):
        Tag.objects.create(name='test tag')
        assert ProtectedClass.objects.count() > 0
        assert HateCrimesandTrafficking.objects.count() > 0
        assert RetentionSchedule.objects.count() > 0

        report = ReportFactory.build()
        report.save()

        activity.send_action(
            User.objects.first(),
            verb="Something happened",
            description="Did some action that has sensitive info to destroy",
            target=report,
        )

        fake_attachment = ReportAttachment.objects.create(
            file=SimpleUploadedFile('test.txt', b'test'),
            filename='test.txt',
            report=report)
        fake_attachment.save()
        fake_email = TMSEmail.create_fake(report=report, body='foo', html_body='bar')
        fake_email.save()
        fake_internal_comment = CommentAndSummary.objects.create(
            note='note',
            author=User.objects.first(),
        )

        campaign = Campaign.objects.create()

        report.save()

        should_be_deleted = [fake_attachment, fake_email, fake_internal_comment]
        should_not_be_deleted = [campaign]
        assert report.attachments.count() > 0
        assert report.target_actions.count() > 0
        assert report.emails.count() > 0

        cases = [
            ('id', report.id, report.id),
            ('contact_first_name', 'Bob', None),
            ('contact_last_name', 'Smith', None),
            ('contact_email', 'bob.smith@test.com', None),
            ('contact_phone', '555-555-5555', None),
            ('contact_address_line_1', '123 Main St', None),
            ('contact_address_line_2', 'Apt 1', None),
            ('contact_city', 'Anytown', None),
            ('contact_state', 'FL', None),
            ('contact_zip', '12345', None),
            ('contact_inmate_number', '12345', None),

            ('contact_2_kind', 'Bob', None),
            ('contact_2_name', 'Smith', None),
            ('contact_2_email', 'bob.smith@test.com', None),
            ('contact_2_phone', '555-555-5555', None),
            ('contact_2_address_line_1', '123 Main St', None),
            ('contact_2_address_line_2', 'Apt 1', None),
            ('contact_2_city', 'Anytown', None),
            ('contact_2_state', 'FL', None),
            ('contact_2_zip_code', '12345', None),

            ('contact_3_kind', 'Bob', None),
            ('contact_3_name', 'Smith', None),
            ('contact_3_email', 'bob.smith@test.com', None),
            ('contact_3_phone', '555-555-5555', None),
            ('contact_3_address_line_1', '123 Main St', None),
            ('contact_3_address_line_2', 'Apt 1', None),
            ('contact_3_city', 'Anytown', None),
            ('contact_3_state', 'FL', None),
            ('contact_3_zip_code', '12345', None),

            ('contact_4_kind', 'Bob', None),
            ('contact_4_name', 'Smith', None),
            ('contact_4_email', 'bob.smith@test.com', None),
            ('contact_4_phone', '555-555-5555', None),
            ('contact_4_address_line_1', '123 Main St', None),
            ('contact_4_address_line_2', 'Apt 1', None),
            ('contact_4_city', 'Anytown', None),
            ('contact_4_state', 'FL', None),
            ('contact_4_zip_code', '12345', None),

            ('eeoc_charge_number', '123-123-1234', None),
            ('eeoc_office', EeocOffice.objects.filter(id=1).first(), None),

            ('emails', report.emails.all(), []),

            ('by_repeat_writer', True, False),
            ('servicemember', True, None),
            ('primary_complaint', 'housing', ''),
            ('hate_crime', 'yes', None),
            ('dj_number', '170-80-1234', None),
            ('protected_class', ProtectedClass.objects.all(), []),
            ('other_class', 'Other protected class', None),

            ('violation_summary', 'Summary of violation', None),
            ('status', 'closed', 'new'),
            ('report_disposition_status', 'approved', None),
            ('assigned_section', 'DRS', 'ADM'),
            ('working_group', None, 'VOT', 'ELS-CRU'),

            ('location_name', 'Test Location', None),
            ('location_address_line_1', '123 Main St', None),
            ('location_address_line_2', 'Apt 1', None),
            ('location_city_town', 'Anytown', None),
            ('location_state', 'FL', None),
            ('location_zipcode', '12345', None),

            ('election_details', 'federal', None),
            ('public_or_private_employer', 'private_employer', None),
            ('employer_size', '14_or_less', None),
            ('public_or_private_school', 'public_school', None),
            ('inside_correctional_facility', 'inside', None),
            ('correctional_facility_type', 'federal', None),
            ('commercial_or_public_place', 'place_of_worship', None),
            ('other_commercial_or_public_place', 'etc etc', None),
            ('public_or_private_school', 'public', None),

            ('last_incident_year', 2024, None),
            ('last_incident_day', 31, None),
            ('last_incident_month', 12, None),

            ('internal_comments', [fake_internal_comment], []),

            ('district', '80', None),
            ('primary_statute', '170', None),

            ('origination_utm_source', 'utm_source', None),
            ('origination_utm_medium', 'utm_medium', None),
            ('origination_utm_campaign', campaign, None),
            ('unknown_origination_utm_campaign', 'utm_campaign', None),
            ('origination_utm_term', 'utm_term', None),
            ('origination_utm_content', 'utm_content', None),

            ('tags', Tag.objects.all(), []),

            ('public_id', '123456-ABC', '123456-ABC'),
            ('create_date', datetime.datetime.now(), datetime.datetime.fromtimestamp(0)),
            ('crt_reciept_year', 2024, None),
            ('crt_reciept_day', 31, None),
            ('crt_reciept_month', 10, None),
            ('intake_format', 'phone', None),
            ('author', 'Foo', None),
            ('assigned_to', User.objects.first(), None),

            ('closed_date', datetime.datetime.now(), None),
            ('language', 'es', None),

            ('viewed', True, False),
            ('batched_for_disposal', True, True),
            ('disposed', True, True),
            ('hatecrimes_trafficking', HateCrimesandTrafficking.objects.all(), []),

            ('referred', True, False),
            ('referral_section', 'DRS', ''),

            ('litigation_hold', False, False),
            ('retention_schedule', RetentionSchedule.objects.first(), RetentionSchedule.objects.first()),

            ('violation_summary_search_vector', 'Summary of report', None),

            ('attachments', report.attachments.all(), []),
            ('target_actions', report.target_actions.all(), []),
            ('actor_actions', [], []),
            ('action_object_actions', [], []),
        ]

        all_fields = set(field.name for field in Report._meta.get_fields())
        accounted_fields = set(field for field, _, _ in cases)
        ignored_fields = {'modified_date', 'email_report_count'}
        missing_fields = all_fields - ignored_fields - accounted_fields
        self.assertEqual(len(missing_fields), 0, msg=f'The following fields were not explicitly accounted for in disposal tests: {missing_fields}')

        for field, actual, expected in cases:
            try:
                setattr(report, field, actual)
            except TypeError:  # Happens with many-to-many fields
                getattr(report, field).set(actual)
        report.save()

        report.redact()

        for field, _, expected in cases:
            after = getattr(report, field)
            if isinstance(expected, list):
                after = list(after.all())
            self.assertEqual(after, expected, msg=f'Field {field} was {after} but should have been {expected}')

        for deletable in should_be_deleted:
            self.assertFalse(deletable.__class__.objects.filter(pk=deletable.pk).exists(), msg=f'{deletable} was not deleted')

        for undeletable in should_not_be_deleted:
            self.assertTrue(undeletable.__class__.objects.filter(pk=undeletable.pk).exists(), msg=f'{undeletable} was deleted')
