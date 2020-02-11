import secrets
from datetime import date, timedelta
import copy

from testfixtures import LogCapture

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import ProtectedClass, Report, HateCrimesandTrafficking
from .model_variables import (
    PROTECTED_CLASS_CHOICES,
    PROTECTED_CLASS_ERROR,
    VIOLATION_SUMMARY_ERROR,
    WHERE_ERRORS,
    PRIMARY_COMPLAINT_CHOICES,
    PRIMARY_COMPLAINT_ERROR,
    HATE_CRIMES_TRAFFICKING_CHOICES,
    SERVICEMEMBER_ERROR,
)
from .forms import (
    Who,
    Details,
    Contact,
    ProtectedClassForm,
    LocationForm,
    PrimaryReason,
    CommercialPublicLocation,
    EducationLocation,
    PoliceLocation,
    When,
)
from .test_data import SAMPLE_REPORT


class Valid_Form_Tests(TestCase):
    def setUp(self):
        for choice in PROTECTED_CLASS_CHOICES:
            ProtectedClass.objects.get_or_create(protected_class=choice)

    """Confirms each form is valid when given valid test data."""

    def test_Who_valid(self):
        form = Who(data={
            'respondent_contact_ask': False,
            'respondent_type': 'employer',
            'respondent_name': 'Max',
            'respondent_city': 'Hometown',
            'respondent_state': 'AK',
        })
        self.assertTrue(form.is_valid())

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
        self.assertEquals(
            form.errors,
            {
                'location_name': [errors['location_name']],
                'location_state': [errors['location_state']],
                'location_city_town': [errors['location_city_town']],
            }
        )

    def test_Class_valid(self):
        form = ProtectedClassForm(data={
            'protected_class': ProtectedClass.objects.all(),
            'other_class': 'Random string under 150 characters (हिन्दी)',
        })
        self.assertTrue(form.is_valid())

    def test_Primary_reason_valid(self):
        form = PrimaryReason(data={
            'hatecrimes_trafficking': HateCrimesandTrafficking.objects.all(),
            'primary_complaint': PRIMARY_COMPLAINT_CHOICES[0][0],
        })
        self.assertTrue(form.is_valid())

    def test_When_vaild(self):
        form = When(data={
            'last_incident_year': 2019,
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertTrue(form.is_valid())


class Valid_CRT_view_Tests(TestCase):
    def setUp(self):
        for choice in PROTECTED_CLASS_CHOICES:
            ProtectedClass.objects.get_or_create(protected_class=choice)
        test_report = Report.objects.create(**SAMPLE_REPORT)
        test_report.last_incident_day = '1'
        test_report.last_incident_month = '1'
        test_report.last_incident_year = '2020'
        self.protected_example = ProtectedClass.objects.get(protected_class=PROTECTED_CLASS_CHOICES[0])
        test_report.protected_class.add(self.protected_example)
        test_report.save()
        self.test_report = test_report
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.content = str(response.content)

    def tearDown(self):
        self.user.delete()

    def test_incident_date(self):
        print(self.content)
        print(self.test_report.last_incident_day)
        self.assertTrue('1/1/2020' in self.content)

    def test_first_name(self):
        self.assertTrue(self.test_report.contact_first_name in self.content)

    def test_last_name(self):
        self.assertTrue(self.test_report.contact_last_name in self.content)

    def test_email(self):
        self.assertTrue(self.test_report.contact_email in self.content)

    def test_phone(self):
        self.assertTrue(self.test_report.contact_phone in self.content)

    def test_violation_summary(self):
        # formatting the summary is done in the template
        self.assertTrue(self.test_report.violation_summary[:119] in self.content)

    def test_incident_location(self):
        self.assertTrue(self.test_report.location_city_town in self.content)
        self.assertTrue(self.test_report.location_state in self.content)

    def test_auto_section_assignment(self):
        # move this to the section assignment once there are clear rules of when it should be assigned to ADM
        self.assertTrue('ADM' in self.content)


class Complaint_Show_View_404(TestCase):
    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

    def tearDown(self):
        self.user.delete()

    def test_404_on_non_existant_record(self):
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': '1'}))
        self.assertEqual(response.status_code, 404)


class Complaint_Show_View_Valid(TestCase):
    def setUp(self):
        SAMPLE_REPORT['primary_complaint'] = 'voting'
        SAMPLE_REPORT['election_details'] = 'federal'

        test_report = Report.objects.create(**SAMPLE_REPORT)

        for choice in PROTECTED_CLASS_CHOICES:
            pc = ProtectedClass.objects.get_or_create(protected_class=choice)
            test_report.protected_class.add(pc[0])
            test_report.save()

        for choice in HATE_CRIMES_TRAFFICKING_CHOICES:
            hct = HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option=choice)
            test_report.hatecrimes_trafficking.add(hct[0])
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
        self.assertTrue(self.context['crimes']['physical_harm'])
        self.assertTrue(self.context['crimes']['trafficking'])
        self.assertTrue(self.test_report.location_name in self.content)
        self.assertTrue(self.test_report.location_city_town in self.content)
        self.assertTrue(self.test_report.location_state in self.content)

    def test_full_summary(self):
        self.assertTrue(self.test_report.violation_summary in self.content)


class SectionAssignmentTests(TestCase):
    def test_CRM_routing(self):
        # All human trafficking goes to CRM.
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        human_trafficking = HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option='Coerced or forced to do work or perform a commercial sex act')
        test_report.hatecrimes_trafficking.add(human_trafficking[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'CRM')

        # All hate crime goes to CRM.
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        test_report = Report.objects.create(**SAMPLE_REPORT)
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')
        test_report.protected_class.add(disability[0])
        human_trafficking = HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option='Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability')
        test_report.hatecrimes_trafficking.add(human_trafficking[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'CRM')

        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'outside'
        test_report = Report.objects.create(**data)
        self.assertTrue(test_report.assign_section() == 'CRM')

        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() != 'CRM')

    def test_VOT_routing(self):
        # Unless a protected class of disability is selected, reports
        # with a primary complaint of voting should be assigned to voting.
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'VOT')

    def test_ELS_routing(self):
        # Workplace discrimination complaints are routed to ELS by default
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'workplace'
        test_report = Report.objects.create(**data)
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'ELS')

        data = copy.deepcopy(SAMPLE_REPORT)
        SAMPLE_REPORT['primary_complaint'] = 'workplace'
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'ELS')

    def test_IER_routing(self):
        # If the report contains any of the first three Protected Classes here,
        # route to IER
        immigration = ProtectedClass.objects.get_or_create(protected_class='Immigration/citizenship status (choosing this will not share your status)')
        language = ProtectedClass.objects.get_or_create(protected_class='Language')
        origin = ProtectedClass.objects.get_or_create(protected_class='National origin (including ancestry and ethnicity)')

        SAMPLE_REPORT['primary_complaint'] = 'workplace'
        test_report = Report.objects.create(**SAMPLE_REPORT)

        test_report.protected_class.add(immigration[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'IER')

        test_report.protected_class.remove(immigration[0])
        test_report.protected_class.add(language[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'IER')

        test_report.protected_class.remove(language[0])
        test_report.protected_class.add(origin[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'IER')

    def test_HCE_routing(self):
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'commercial_or_public'
        test_report = Report.objects.create(**data)
        self.assertTrue(test_report.assign_section() == 'HCE')

        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'housing'
        test_report = Report.objects.create(**data)
        self.assertTrue(test_report.assign_section() == 'HCE')

        data = copy.deepcopy(SAMPLE_REPORT)
        test_report.commercial_or_public_place = 'other'
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'HCE')

    def test_EOS_routing(self):
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')

        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'education'
        data['public_or_private_school'] = 'public'
        test_report = Report.objects.create(**data)
        self.assertTrue(test_report.assign_section() == 'EOS')

        test_report.public_or_private_school = 'private'
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'EOS')

        test_report.protected_class.add(disability[0])
        test_report.public_or_private_school = 'public'
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'EOS')

    def test_SPL_routing(self):
        # Test if law enforcement and inside a prison
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'inside'
        test_report = Report.objects.create(**data)
        self.assertTrue(test_report.assign_section() == 'SPL')

        test_report.primary_complaint = 'commercial_or_public'
        test_report.commercial_or_public_place = 'healthcare'
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'SPL')

    def test_DRS_routing(self):
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')

        school_data = copy.deepcopy(SAMPLE_REPORT)
        school_data['primary_complaint'] = 'education'
        school_data['public_or_private_school'] = 'private'
        test_report = Report.objects.create(**school_data)
        test_report.protected_class.add(disability[0])
        self.assertTrue(test_report.assign_section() == 'DRS')

        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'something_else'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        self.assertTrue(test_report.assign_section() == 'DRS')

        # housing exemption
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'commercial_or_public'
        data['commercial_or_public_place'] = 'healthcare'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        self.assertTrue(test_report.assign_section() == 'DRS')

        # Reports with a primary complaint of voting and protected class of disability
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**data)
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'DRS')

        # special exemptions
        data = copy.deepcopy(SAMPLE_REPORT)
        data['primary_complaint'] = 'police'
        data['inside_correctional_facility'] = 'inside'
        test_report = Report.objects.create(**data)

        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'DRS')

        test_report.inside_correctional_facility = 'outside'
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'DRS')


class Valid_CRT_Pagnation_Tests(TestCase):
    def setUp(self):
        for choice in PROTECTED_CLASS_CHOICES:
            pc = ProtectedClass.objects.get_or_create(protected_class=choice)
            test_report = Report.objects.create(**SAMPLE_REPORT)
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
        num_records = len(PROTECTED_CLASS_CHOICES)
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
        self.assertTrue(f'Go to page {len(PROTECTED_CLASS_CHOICES)}.' in content)
        # link generation, update with sorting etc. as we add
        self.assertTrue('href="?per_page=1' in content)
        self.assertTrue('sort=assigned_section' in content)


class Valid_CRT_SORT_Tests(TestCase):
    def setUp(self):
        for choice in PRIMARY_COMPLAINT_CHOICES:
            SAMPLE_REPORT['primary_complaint'] = choice[0]
            test_report = Report.objects.create(**SAMPLE_REPORT)
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
            SAMPLE_REPORT['primary_complaint'] = choice[0]
            test_report = Report.objects.create(**SAMPLE_REPORT)
            test_report.assigned_section = test_report.assign_section()
            test_report.save()

        SAMPLE_REPORT['primary_complaint'] = PRIMARY_COMPLAINT_CHOICES[0][0]
        test_report = Report.objects.create(**SAMPLE_REPORT)
        test_report.contact_first_name = 'Mary'
        test_report.contact_last_name = 'Bar'
        test_report.location_city_town = 'Cleveland'
        test_report.location_state = 'OH'
        test_report.assigned_section = test_report.assign_section()
        test_report.save()

        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.url_base = reverse('crt_forms:crt-forms-index')
        self.len_all_results = len(self.client.get(self.url_base).context['data_dict'])

    def tearDown(self):
        self.user.delete()

    def test_filter(self):
        url = f'{self.url_base}?assigned_section=ADM'
        one_filter_response = self.client.get(url)
        expected_reports = Report.objects.filter(assigned_section='ADM')
        actual_reports = one_filter_response.context['data_dict']

        self.assertTrue(len(actual_reports) == len(list(expected_reports)))

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

        url_start_yesterday = f"{self.url_base}?create_date_start={yesterday.strftime('%Y%m%d')}"
        start_yesterday_response = self.client.get(url_start_yesterday).context['data_dict']

        url_start_tomorrow = f"{self.url_base}?create_date_start={tomorrow.strftime('%Y%m%d')}"
        start_tomorrow_response = self.client.get(url_start_tomorrow).context['data_dict']

        url_end_yesterday = f"{self.url_base}?create_date_end={yesterday.strftime('%Y%m%d')}"
        end_yesterday_response = self.client.get(url_end_yesterday).context['data_dict']

        url_end_tomorrow = f"{self.url_base}?create_date_end={tomorrow.strftime('%Y%m%d')}"
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

        self.assertEqual(len(phrase_response), self.len_all_results)
        self.assertEqual(len(case_insensitive_phrase_response), self.len_all_results)
        self.assertEqual(len(disjointed_phrase_response), self.len_all_results)
        self.assertEqual(len(url_not_in_phrase_response), 0)

    def test_first_name_filter(self):
        first_name_filter = 'contact_first_name=lin'
        response = self.client.get(f'{self.url_base}?{first_name_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEquals(report_len, self.len_all_results - 1)

    def test_last_name_filter(self):
        last_name_filter = 'contact_last_name=bar'
        response = self.client.get(f'{self.url_base}?{last_name_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEquals(report_len, 1)

    def test_city_name_filter(self):
        city_name_filter = 'location_city_town=land'
        response = self.client.get(f'{self.url_base}?{city_name_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEquals(report_len, 1)

    def test_state_filter(self):
        state_filter = 'location_state=OH'
        response = self.client.get(f'{self.url_base}?{state_filter}')
        reports = response.context['data_dict']

        report_len = len(reports)

        self.assertEquals(report_len, 1)


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

    def test_required_primary_reason_hatecrime(self):
        form = PrimaryReason(data={
            'hatecrimes_trafficking_set': None,
            'primary_complaint': '',
        })
        # ensure Hatecrime is not in error list
        self.assertFalse('hatecrimes_trafficking<ul class="errorlist"><li>' in str(form.errors))
        self.assertTrue(f'<ul class="errorlist"><li>{PRIMARY_COMPLAINT_ERROR}' in str(form.errors))

    def test_required_servicemember(self):
        form = Contact(data={})
        self.assertTrue(f'<ul class="errorlist"><li>{SERVICEMEMBER_ERROR}' in str(form.errors))

    def test_required_year(self):
        form = When(data={
            'last_incident_month': 5,
            'last_incident_day': 5,
        })
        self.assertTrue(f'<ul class="errorlist"><li>Please enter a year' in str(form.errors))

    def test_required_month(self):
        form = When(data={
            'last_incident_year': 2019,
            'last_incident_day': 5,
        })
        self.assertTrue(f'<ul class="errorlist"><li>Please enter a month' in str(form.errors))

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

    def test_commercial_public_place(self):
        location_data = {
            'location_name': 'Street',
            'location_city_town': 'Nome',
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
            'location_city_town': 'Nome',
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
        self.assertEquals(
            form.errors,
            {'contact_phone': ['Enter a valid value.']}
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
            self.assertTrue(phone_error_message == ['Enter a valid value.'])

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
        test_report = Report.objects.create(**SAMPLE_REPORT)
        test_report.contact_first_name = 'Foobert'
        test_report.contact_last_name = 'Bar'
        test_report.location_city_town = 'Cleveland'
        test_report.location_state = 'OH'
        test_report.assigned_section = test_report.assign_section()
        test_report.status = 'new'
        test_report.save()

        self.test_report = test_report
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

    def tearDown(self):
        self.user.delete()

    def test_update_status_property(self):
        self.assertTrue(self.test_report.status == 'new')
        response = self.client.post(reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id}), {'status': 'open'})
        print(response.context)
        self.assertTrue(response.context['data'].status == 'open')

    def test_update_assigned_section_property(self):
        response = self.client.post(reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id}), {'assigned_section': 'VOT'})

        self.assertTrue(response.context['data'].assigned_section == 'VOT')


class LoginRequiredTests(TestCase):
    """Please add a test for each url that is tied to a view that requires authorization/authentication."""

    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'lennon@thebeatles.com', self.test_pass)
        test_report = Report.objects.create(**SAMPLE_REPORT)
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

            create = 'cts_forms.signals', 'INFO', 'ADMIN ACTION by: CLI CLI @ CLI User saved: {pk} permissions: <QuerySet []> staff: False superuser: False active: True'.format(pk=self.user2_pk)
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
