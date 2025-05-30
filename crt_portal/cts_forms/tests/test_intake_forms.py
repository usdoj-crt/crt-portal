"""
Tests for:
 - public form
 - pro form
"""
import copy
import secrets

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ..forms import (
    CommercialPublicLocation, ComplaintActions, Contact,
    Details, EducationLocation, WorkplaceLocation, LocationForm,
    PoliceLocation, PrimaryReason, ProfileForm, ProForm,
    ProtectedClassForm, When, save_form, maybe_auto_close, maybe_auto_reroute
)
from ..model_variables import (
    CONTACT_PHONE_INVALID_MESSAGE,
    INTAKE_FORMAT_ERROR,
    PRIMARY_COMPLAINT_CHOICES,
    PRIMARY_COMPLAINT_ERROR, PROTECTED_CLASS_ERROR,
    PROTECTED_MODEL_CHOICES, SERVICEMEMBER_ERROR,
    VIOLATION_SUMMARY_ERROR, WHERE_ERRORS, DATE_ERRORS
)
from ..models import CommentAndSummary, ProtectedClass, Report, Campaign, get_system_user, SavedSearch
from .test_data import SAMPLE_REPORT_1
from .factories import UserFactory


class Valid_Form_Tests(TestCase):
    """Confirms each form is valid when given valid test data."""

    def setUp(self):
        for choice, label in PROTECTED_MODEL_CHOICES:
            ProtectedClass.objects.get_or_create(value=choice)

    def test_Details_valid(self):
        form = Details(data={
            'violation_summary': 'Hello! I have a problem. ႠႡႢ',
        })
        self.assertTrue(form.is_valid())

    def test_Contact_valid(self):
        form = Contact(data={
            'contact_first_name': 'first_name',
            'contact_last_name': 'last_name',
            'servicemember': 'yes',
        })
        self.assertTrue(form.is_valid())

    def test_Location_valid(self):
        form = LocationForm(data={
            'location_name': 'Beach',
            'location_address_line_1': '',
            'location_address_line_2': '',
            'location_city_town': 'Bethany',
            'location_state': 'DE',
        })
        self.assertTrue(form.is_valid())

    def test_Location_invalid(self):
        form = LocationForm(data={
            'location_name': '',
            'location_address_line_1': '',
            'location_address_line_2': '',
            'location_city_town': '',
            'location_state ': '',
        })
        errors = dict(WHERE_ERRORS)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'location_name': [errors['location_name']],
                'location_state': [errors['location_state']],
                'location_city_town': [errors['location_city_town']],
            }
        )

    def test_Class_valid(self):
        form = ProtectedClassForm({
            'protected_class': ProtectedClass.active_choices.all(),
            'other_class': 'Random string under 150 characters (हिन्दी)',
        })
        self.assertTrue(form.is_valid())

    def test_Primary_reason_valid(self):
        form = PrimaryReason(data={
            'primary_complaint': PRIMARY_COMPLAINT_CHOICES[0][0],
        })
        self.assertTrue(form.is_valid())

    # Note: a more complete suite of date validation tests are in
    # `Valid_Form_Tests` below
    def test_When_valid(self):
        form = When(data={
            'last_incident_year': 2019,
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertTrue(form.is_valid())

    def test_profile_update_valid(self):
        form = ProfileForm(data={
            'intake_filters': ['VOT', 'ADM']
        })
        self.assertTrue(form.is_valid())


class Valid_CRT_view_Tests(TestCase):
    def setUp(self):
        for choice, label in PROTECTED_MODEL_CHOICES:
            ProtectedClass.objects.get_or_create(value=choice)
        test_report = Report.objects.create(**SAMPLE_REPORT_1)
        test_report.last_incident_day = '1'
        test_report.last_incident_month = '1'
        test_report.last_incident_year = '2020'
        self.protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[0][0])
        test_report.protected_class.add(self.protected_example)
        test_report.save()
        self.test_report = test_report
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.content = str(response.content)

    def tearDown(self):
        self.user.delete()

    def test_incident_date(self):
        self.assertTrue('1/1/2020' in self.content)

    def test_first_name(self):
        self.assertTrue(self.test_report.contact_first_name in self.content)

    def test_last_name(self):
        self.assertTrue(self.test_report.contact_last_name in self.content)

    def test_email(self):
        self.assertTrue(self.test_report.contact_email in self.content)

    def test_phone(self):
        self.assertTrue(self.test_report.contact_phone in self.content)

    def test_summary(self):
        """Report table renders internal summary"""
        summary_text = "Internal summary test"
        summary = CommentAndSummary(is_summary=True, note=summary_text)
        summary.save()
        self.test_report.internal_comments.add(summary)

        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.assertContains(response, summary_text)

    def test_incident_location(self):
        self.assertTrue(self.test_report.location_city_town in self.content)
        self.assertTrue(self.test_report.location_state in self.content)

    def test_auto_section_assignment(self):
        # move this to the section assignment once there are clear rules of when it should be assigned to ADM
        self.assertTrue('ADM' in self.content)


class OriginationDataTests(TestCase):
    """Ensures that origination (utm, etc) data makes it into the database."""

    def setUp(self):
        self.campaign = Campaign.objects.create(internal_name="Fake Campaign")

    def tearDown(self):
        self.campaign.delete()

    def test_form_works_without_codes(self):
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 200)

    def test_form_captures_params(self):
        response = self.client.get(
            '/report/',
            {
                'utm_source': 'mock-source',
                'utm_medium': 'mock-medium',
                'utm_campaign': self.campaign.uuid,
                'utm_term': 'mock-term',
                'utm_content': 'mock-content',
            })

        self.assertEqual(response.status_code, 200)
        expected_template = '<input type="hidden" name="0-{field}" value="{mock}" id="id_0-{field}">'
        self.assertInHTML(
            expected_template.format(
                field='origination_utm_source', mock='mock-source'), response.content.decode())
        self.assertInHTML(
            expected_template.format(
                field='origination_utm_medium', mock='mock-medium'), response.content.decode())
        self.assertInHTML(
            expected_template.format(
                field='origination_utm_campaign', mock=self.campaign.uuid), response.content.decode())
        self.assertInHTML(
            expected_template.format(
                field='origination_utm_term', mock='mock-term'), response.content.decode())
        self.assertInHTML(
            expected_template.format(
                field='origination_utm_content', mock='mock-content'), response.content.decode())

    def test_form_captures_unknown_campaigns(self):
        response = self.client.get(
            '/report/',
            {
                'utm_campaign': 'ohno-campaign',
            })

        self.assertEqual(response.status_code, 200)
        expected_template = '<input type="hidden" name="0-{field}" value="{mock}" id="id_0-{field}">'
        self.assertInHTML(
            expected_template.format(
                field='unknown_origination_utm_campaign', mock='ohno-campaign'), response.content.decode())

    def test_captured_params_are_saved(self):
        form_data_dict = {
            **copy.deepcopy(SAMPLE_REPORT_1),
            'protected_class': ProtectedClass.objects.none(),
            'origination_utm_source': 'mock-source',
            'origination_utm_medium': 'mock-medium',
            'origination_utm_campaign': self.campaign,
            'origination_utm_term': 'mock-term',
            'origination_utm_content': 'mock-content',
        }
        _, saved_object = save_form(form_data_dict, intake_format='web')
        self.assertEqual(saved_object.origination_utm_source, 'mock-source')
        self.assertEqual(saved_object.origination_utm_medium, 'mock-medium')
        self.assertEqual(saved_object.origination_utm_campaign, self.campaign)
        self.assertEqual(saved_object.origination_utm_term, 'mock-term')
        self.assertEqual(saved_object.origination_utm_content, 'mock-content')

    def test_unknown_campaign_is_saved(self):
        form_data_dict = {
            **copy.deepcopy(SAMPLE_REPORT_1),
            'protected_class': ProtectedClass.objects.none(),
            'unknown_origination_utm_campaign': 'ohno-campaign',
        }
        _, saved_object = save_form(form_data_dict, intake_format='web')
        self.assertEqual(saved_object.unknown_origination_utm_campaign, 'ohno-campaign')


class RoutingOverrideTests(TestCase):
    def setUp(self):
        self.search = SavedSearch.objects.create(
            name='test search',
            query='status=new&status=open&violation_summary=%22foo!%22&no_status=false&grouping=default',
            override_section_assignment=True,
            override_section_assignment_with='DRS',
        )
        self.matching_report = Report.objects.create(**{**SAMPLE_REPORT_1, 'violation_summary': 'foo!'})
        self.nonmatching_report = Report.objects.create(**{**SAMPLE_REPORT_1, 'violation_summary': 'bar!'})

    def test_maybe_auto_reroute_reroutes_matching(self):
        maybe_auto_reroute(self.matching_report)

        self.matching_report.refresh_from_db()

        self.assertEqual(self.matching_report.assigned_section, 'DRS')
        actions = self.matching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'Routing overridden' in a.verb), None)
        self.assertIsNotNone(action, 'No acstream found for rerouted report')
        self.assertEqual(action.actor, get_system_user())
        self.assertEqual(action.verb, 'Routing overridden')
        self.assertEqual(action.description, 'Rerouted to DRS due to Saved Search test search')

    def test_maybe_auto_reroute_skips_nonmatching(self):
        maybe_auto_reroute(self.nonmatching_report)

        self.nonmatching_report.refresh_from_db()
        self.assertEqual(self.nonmatching_report.status, 'new')
        actions = self.nonmatching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'Routing overridden' in a.verb), None)
        self.assertIsNone(action)

    def test_maybe_auto_reroute_only_reroutes_if_enabled(self):
        self.search.override_section_assignment = False
        self.search.save()
        maybe_auto_reroute(self.matching_report)

        self.matching_report.refresh_from_db()

        self.assertEqual(self.matching_report.status, 'new')
        actions = self.matching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'Routing overridden' in a.verb), None)
        self.assertIsNone(action)


class AutoCloseTests(TestCase):
    def setUp(self):
        self.search = SavedSearch.objects.create(
            name='test search',
            query='status=new&status=open&violation_summary=%22foo!%22&no_status=false&grouping=default',
            auto_close=True,
            auto_close_reason='foo happened!',
        )
        self.matching_report = Report.objects.create(**{**SAMPLE_REPORT_1, 'violation_summary': 'foo!'})
        self.nonmatching_report = Report.objects.create(**{**SAMPLE_REPORT_1, 'violation_summary': 'bar!'})

    def test_maybe_auto_close_closes_matching(self):
        maybe_auto_close(self.matching_report)

        self.matching_report.refresh_from_db()

        self.assertEqual(self.matching_report.status, 'closed')
        actions = self.matching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'auto-closed' in a.verb), None)
        self.assertIsNotNone(action, 'No acstream found for auto-closed report')
        self.assertEqual(action.actor, get_system_user())
        self.assertEqual(action.verb, 'Report auto-closed')
        self.assertEqual(action.description, 'Report automatically closed on submission because foo happened!')

    def test_maybe_auto_close_skips_nonmatching(self):
        maybe_auto_close(self.nonmatching_report)

        self.nonmatching_report.refresh_from_db()
        self.assertEqual(self.nonmatching_report.status, 'new')
        actions = self.nonmatching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'auto-closed' in a.description), None)
        self.assertIsNone(action)

    def test_maybe_auto_close_only_closes_if_enabled(self):
        self.search.auto_close = False
        self.search.save()
        maybe_auto_close(self.matching_report)

        self.matching_report.refresh_from_db()

        self.assertEqual(self.matching_report.status, 'new')
        actions = self.matching_report.target_actions.all().prefetch_related('actor')
        action = next((a for a in actions if 'auto-closed' in a.description), None)
        self.assertIsNone(action)


class SectionAssignmentTests(TestCase):
    def test_CRM_routing(self):
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'outside'
        test_report = Report.objects.create(**data)
        self.assertEqual(test_report.assign_section(), 'CRM')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        disability = ProtectedClass.objects.get_or_create(value='disability')
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertNotEqual(test_report.assign_section(), 'CRM')

    def test_VOT_routing(self):
        # Unless a protected class of disability is selected, reports
        # with a primary complaint of voting should be assigned to voting.
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'VOT')

    def test_ELS_routing(self):
        # Workplace discrimination complaints are routed to ELS by default
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'workplace'
        test_report = Report.objects.create(**data)
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'ELS')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        SAMPLE_REPORT_1['primary_complaint'] = 'workplace'
        disability = ProtectedClass.objects.get_or_create(value='disability')
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'ELS')

    def test_IER_routing(self):
        # If the report contains any of the first three Protected Classes here,
        # route to IER
        immigration = ProtectedClass.objects.get_or_create(value='immigration')
        language = ProtectedClass.objects.get_or_create(value='language')
        origin = ProtectedClass.objects.get_or_create(value='national_origin')

        SAMPLE_REPORT_1['primary_complaint'] = 'workplace'
        test_report = Report.objects.create(**SAMPLE_REPORT_1)

        test_report.protected_class.add(immigration[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'IER')

        test_report.protected_class.remove(immigration[0])
        test_report.protected_class.add(language[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'IER')

        test_report.protected_class.remove(language[0])
        test_report.protected_class.add(origin[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'IER')

    def test_HCE_routing(self):
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'commercial_or_public'
        test_report = Report.objects.create(**data)
        self.assertEqual(test_report.assign_section(), 'HCE')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'housing'
        test_report = Report.objects.create(**data)
        self.assertEqual(test_report.assign_section(), 'HCE')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        test_report.commercial_or_public_place = 'other'
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'HCE')

    def test_EOS_routing(self):
        disability = ProtectedClass.objects.get_or_create(value='disability')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'education'
        data['public_or_private_school'] = 'public'
        test_report = Report.objects.create(**data)
        self.assertEqual(test_report.assign_section(), 'EOS')

        test_report.public_or_private_school = 'private'
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'EOS')

        test_report.protected_class.add(disability[0])
        test_report.public_or_private_school = 'public'
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'EOS')

    def test_SPL_routing(self):
        # Test if law enforcement and inside a prison
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'inside'
        test_report = Report.objects.create(**data)
        self.assertEqual(test_report.assign_section(), 'SPL')

        test_report.primary_complaint = 'commercial_or_public'
        test_report.commercial_or_public_place = 'healthcare'
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'SPL')

    def test_DRS_routing(self):
        disability = ProtectedClass.objects.get_or_create(value='disability')

        school_data = copy.deepcopy(SAMPLE_REPORT_1)
        school_data['primary_complaint'] = 'education'
        school_data['public_or_private_school'] = 'private'
        test_report = Report.objects.create(**school_data)
        test_report.protected_class.add(disability[0])
        self.assertEqual(test_report.assign_section(), 'DRS')

        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'something_else'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        self.assertEqual(test_report.assign_section(), 'DRS')

        # housing exemption
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'commercial_or_public'
        data['commercial_or_public_place'] = 'healthcare'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        self.assertEqual(test_report.assign_section(), 'DRS')

        # Reports with a primary complaint of voting and protected class of disability
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'DRS')

        # special exemptions
        data = copy.deepcopy(SAMPLE_REPORT_1)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'inside'
        test_report = Report.objects.create(**data)

        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'DRS')

        test_report.inside_correctional_facility = 'outside'
        test_report.save()
        self.assertEqual(test_report.assign_section(), 'DRS')


class Validation_Form_Tests(TestCase):
    """Confirming validation on the server level, required fields etc"""

    def test_required_protected_class(self):
        form = ProtectedClassForm(data={
            'other_class': '',
            'protected_class_set': None,
        })

        self.assertTrue('protected_class<ul class="errorlist"><li>{0}'.format(PROTECTED_CLASS_ERROR)[:13] in str(form.errors))

    def test_required_tests(self):
        form = Details(data={
            'violation_summary': ''
        })
        self.assertTrue(f'<ul class="errorlist"><li>{VIOLATION_SUMMARY_ERROR}' in str(form.errors))

    def test_required_primary_reason(self):
        form = PrimaryReason(data={
            'primary_complaint': '',
        })
        self.assertTrue(f'<ul class="errorlist"><li>{PRIMARY_COMPLAINT_ERROR}' in str(form.errors))

    def test_required_servicemember(self):
        form = Contact(data={})
        self.assertTrue(f'<ul class="errorlist"><li>{SERVICEMEMBER_ERROR}' in str(form.errors))

    def test_required_year(self):
        form = When(data={
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["year_required"]}' in str(form.errors))

    def test_required_month(self):
        form = When(data={
            'last_incident_year': 2019,
            'last_incident_day': 5,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["month_required"]}' in str(form.errors))

    def test_NOT_required_day(self):
        form = When(data={
            'last_incident_year': 2019,
            'last_incident_month': 5,
        })
        self.assertTrue(form.is_valid())

    def test_future_incident_date(self):
        form = When(data={
            'last_incident_year': 2200,
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertFalse(form.is_valid())

    def test_past_incident_date(self):
        form = When(data={
            'last_incident_year': 20,
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_year_nonnumeric(self):
        form = When(data={
            'last_incident_year': 'xxxx',
            'last_incident_month': 5,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["no_past"]}' in str(form.errors))

    def test_invalid_month_nonnumeric(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 'zz',
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["month_invalid"]}' in str(form.errors))

    def test_invalid_day_nonnumeric(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 5,
            'last_incident_day': 'xx',
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["day_invalid"]}' in str(form.errors))

    def test_invalid_month_too_high(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 13,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["month_invalid"]}' in str(form.errors))

    def test_invalid_day_too_high(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 5,
            'last_incident_day': 32,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["day_invalid"]}' in str(form.errors))

    def test_invalid_month_negative(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': -1,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_day_negative(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 5,
            'last_incident_day': -1,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_month_zero(self):
        form = When(data={
            'last_incident_year': 2021,
            'last_incident_month': 0,
        })
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["month_invalid"]}' in str(form.errors))

    # Note: the form will accept 0 for day (because it's treated as optional?)

    def test_commercial_public_place(self):
        location_data = {
            'location_name': 'Street',
            'location_city_town': 'None',
            'location_state': 'AK',
        }

        location_data.update({
            'commercial_or_public_place': '',
        })
        form = CommercialPublicLocation(data=location_data)
        self.assertFalse(form.is_valid())

        location_data.update({
            'commercial_or_public_place': 'place_of_worship',
        })
        form = CommercialPublicLocation(data=location_data)
        self.assertTrue(form.is_valid())

        location_data.update({
            'commercial_or_public_place': 'other',
            'other_commercial_or_public_place': None
        })
        form = CommercialPublicLocation(data=location_data)
        self.assertTrue(form.is_valid())

        location_data.update({
            'other_commercial_or_public_place': 'Home'
        })
        form = CommercialPublicLocation(data=location_data)
        self.assertTrue(form.is_valid())

    def test_correctional_facility(self):
        location_data = {
            'location_name': 'Street',
            'location_city_town': 'None',
            'location_state': 'AK',
        }

        location_data.update({
            'inside_correctional_facility': ''
        })
        form = PoliceLocation(data=location_data)
        self.assertFalse(form.is_valid())

        location_data.update({
            'inside_correctional_facility': 'outside'
        })
        form = PoliceLocation(data=location_data)
        self.assertTrue(form.is_valid())

        location_data.update({
            'inside_correctional_facility': 'inside',
            'correctional_facility_type': None
        })
        form = PoliceLocation(data=location_data)
        self.assertFalse(form.is_valid())

        location_data.update({
            'inside_correctional_facility': 'inside',
            'correctional_facility_type': 'state_local'
        })
        form = PoliceLocation(data=location_data)
        self.assertTrue(form.is_valid())

    def test_education_location(self):
        form = EducationLocation(data={
            'public_or_private_school': ''
        })
        self.assertFalse(form.is_valid())

    def test_workplace_location(self):
        form = WorkplaceLocation(data={
            'public_or_private_employer': ''
        })
        self.assertFalse(form.is_valid())


class ContactValidationTests(TestCase):
    def test_non_ascii_name(self):
        form = Contact(data={
            'contact_first_name': '李王',
            'contact_last_name': '王-Núñez',
            'contact_email': '',
            'contact_phone': '',
            'servicemember': 'yes',
        })
        self.assertTrue(form.is_valid())

    def test_non_ascii_email(self):
        form = Contact(data={
            'contact_first_name': '',
            'contact_last_name': '',
            'contact_email': 'foo@bär.com',
            'contact_phone': '',
            'servicemember': 'yes',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_phone(self):
        form = Contact(data={
            'contact_first_name': '',
            'contact_last_name': '',
            'contact_email': '',
            'contact_phone': '33333333333333333333333333',
            'servicemember': 'yes',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'contact_phone': [CONTACT_PHONE_INVALID_MESSAGE]}
        )

    def test_phone_too_short(self):
        """Model validation unit tests require testing the model directly"""
        phone = Report(
            contact_phone='202',
        )

        try:
            phone.full_clean()
        except ValidationError as err:
            phone_error_message = err.message_dict['contact_phone']
            self.assertTrue(phone_error_message == [CONTACT_PHONE_INVALID_MESSAGE])

    def test_international_phone(self):
        phone = Report(
            contact_phone='+02071838750',
        )
        try:
            phone.full_clean()
        except ValidationError as err:
            self.assertTrue('contact_phone' not in err.message_dict)

    def test_international_phone_longer(self):
        phone = Report(
            contact_phone='+442071838750',
        )
        try:
            phone.full_clean()
        except ValidationError as err:
            self.assertTrue('contact_phone' not in err.message_dict)

    def test_phone_has_letters(self):
        phone = Report(
            contact_phone='(123) 123-4567 x445',
        )
        try:
            phone.full_clean()
        except ValidationError as err:
            self.assertTrue('contact_phone' in err.message_dict)


class Complaint_Update_Tests(TestCase):

    def setUp(self):
        test_report = Report.objects.create(**SAMPLE_REPORT_1)
        test_report.contact_first_name = 'Foobert'
        test_report.contact_last_name = 'Bar'
        test_report.location_city_town = 'Cleveland'
        test_report.location_state = 'OH'
        test_report.assigned_section = test_report.assign_section()
        test_report.status = 'open'
        test_report.save()

        self.test_report = test_report
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = UserFactory.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.form_data = {'type': ComplaintActions.CONTEXT_KEY}

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id})

    def tearDown(self):
        self.user.delete()

    def test_update_status_property(self):
        self.form_data.update({'status': 'new'})
        self.assertTrue(self.test_report.status == 'open')
        response = self.client.post(self.url, self.form_data, follow=True)
        self.assertTrue(response.context['data'].status == 'new')

    def test_update_assigned_section_property(self):
        self.form_data.update({'assigned_section': 'VOT'})
        response = self.client.post(self.url, self.form_data, follow=True)

        self.assertTrue(response.context['data'].assigned_section == 'VOT')

    def test_if_status_closed_assignee_must_be_empty(self):
        """If status is closed, existing assignee must be removed"""
        self.test_report.assigned_to = self.user
        self.test_report.save()

        self.form_data.update({'status': 'closed'})
        self.client.post(self.url, self.form_data, follow=True)

        self.test_report.refresh_from_db()
        self.assertIsNone(self.test_report.assigned_to)


class ProFormTest(TestCase):
    def setUp(self):
        data_sample = copy.deepcopy(SAMPLE_REPORT_1)
        data_sample.update({
            'contact_address_line_1': '123',
            'contact_address_line_2': 'Apt 234',
            'contact_city': 'test',
            'contact_state': 'CA',
            'contact_zip': '92886',
            'servicemember': 'no',
            'primary_complaint': PRIMARY_COMPLAINT_CHOICES[1][0],
            'location_address_line_1': '12',
            'location_address_line_2': 'apt b',
            'election_details': 'federal',
            'inside_correctional_facility': 'inside',
            'correctional_facility_type': 'state_local',
            'commercial_or_public_place': 'place_of_worship',
            'other_commercial_or_public_place': 'a castle',
            'public_or_private_school': 'private',
            'last_incident_year': 2020,
            'last_incident_day': 2,
            'last_incident_month': 2,
            'crt_reciept_year': 2020,
            'crt_reciept_day': 2,
            'crt_reciept_month': 2,
            'intake_format': 'phone',
        })
        self.data = data_sample

    def test_required_fields(self):
        form = ProForm(data={})
        errors = str(form.errors)
        self.assertTrue(f'<ul class="errorlist"><li>{INTAKE_FORMAT_ERROR}' in errors)
        self.assertTrue(f'<ul class="errorlist"><li>{PRIMARY_COMPLAINT_ERROR}' in errors)
        self.assertTrue("crt_reciept_day" in errors)
        self.assertTrue("crt_reciept_month" in errors)
        self.assertTrue("crt_reciept_year" in errors)
        self.assertFalse(form.is_valid())

    def test_month_validation(self):
        bad_month_data = self.data
        bad_month_data["crt_reciept_month"] = 13
        form = ProForm(data=bad_month_data)
        self.assertTrue(str(DATE_ERRORS['month_invalid']) in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_day_validation(self):
        bad_day_data = self.data
        bad_day_data["crt_reciept_day"] = 32
        form = ProForm(data=bad_day_data)
        self.assertTrue(str(DATE_ERRORS['day_invalid']) in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_receipt_year_validation(self):
        bad_year_data = self.data
        bad_year_data["crt_reciept_year"] = 1899
        form = ProForm(data=bad_year_data)
        self.assertTrue(DATE_ERRORS['crt_no_past'] in str(form.errors))
        self.assertFalse(form.is_valid())
        bad_year_data["crt_reciept_year"] = 3000
        form = ProForm(data=bad_year_data)
        self.assertTrue(str(DATE_ERRORS['no_future']) in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_last_incident_month_validation(self):
        bad_month_data = self.data
        bad_month_data["last_incident_month"] = 22
        form = ProForm(data=bad_month_data)
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["month_invalid"]}' in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_last_incident_day_validation(self):
        bad_day_data = self.data
        bad_day_data["last_incident_day"] = 80
        form = ProForm(data=bad_day_data)
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["day_invalid"]}' in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_last_incident_year_validation(self):
        bad_year_data = self.data
        bad_year_data["last_incident_year"] = 1899
        form = ProForm(data=bad_year_data)
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["no_past"]}' in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_last_incident_no_future_validation(self):
        future_year_data = self.data
        future_year_data["last_incident_year"] = 3001
        form = ProForm(data=future_year_data)
        self.assertTrue(f'<ul class="errorlist"><li>{DATE_ERRORS["no_future"]}' in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_bad_date(self):
        bad_date_data = self.data
        bad_date_data["crt_reciept_month"] = 2
        bad_date_data["crt_reciept_day"] = 30
        form = ProForm(data=bad_date_data)
        self.assertTrue(DATE_ERRORS['crt_not_valid'] in str(form.errors))
        self.assertFalse(form.is_valid())

    def test_full_example(self):
        form = ProForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_multiple_errors(self):
        data = self.data
        data["crt_reciept_year"] = 1900
        data.pop("crt_reciept_day")
        form = ProForm(data=data)
        self.assertTrue(DATE_ERRORS['day_required'] in str(form.errors))
        self.assertTrue(DATE_ERRORS['crt_no_past'] in str(form.errors))
        self.assertFalse(form.is_valid())


class TestIntakeFormat(TestCase):
    def setUp(self):
        self.form_data_dict = copy.deepcopy(SAMPLE_REPORT_1)
        self.form_data_dict['protected_class'] = ProtectedClass.objects.none()

    def test_intake_save_web(self):
        data, saved_object = save_form(self.form_data_dict, intake_format='web')
        self.assertEqual(saved_object.intake_format, 'web')

    def test_intake_save_ProForm(self):
        form_data_dict = copy.deepcopy(self.form_data_dict)
        form_data_dict['intake_format'] = 'phone'
        data, saved_object = save_form(form_data_dict)
        self.assertEqual(saved_object.intake_format, 'phone')
