import secrets

from testfixtures import LogCapture

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import ProtectedClass, Report, HateCrimesandTrafficking
from .model_variables import PROTECTED_CLASS_CHOICES, PROTECTED_CLASS_ERROR, PROTECTED_CLASS_CODES, VIOLATION_SUMMARY_ERROR, WHERE_ERRORS, PRIMARY_COMPLAINT_CHOICES, PRIMARY_COMPLAINT_ERROR
from .forms import Who, Details, Contact, ProtectedClassForm, LocationForm, PrimaryReason
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
            'when': 'last_6_months',
            'how_many': 'no',
        })
        self.assertTrue(form.is_valid())

    def test_Contact_valid(self):
        form = Contact(data={
            'contact_first_name': 'first_name',
            'contact_last_name': 'last_name',
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


class Valid_CRT_view_Tests(TestCase):
    def setUp(self):
        for choice in PROTECTED_CLASS_CHOICES:
            ProtectedClass.objects.get_or_create(protected_class=choice)
        test_report = Report.objects.create(**SAMPLE_REPORT)
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

    def test_other_class(self):
        self.assertTrue('test other' in self.content)

    def test_class(self):
        # uses the short hand code for display
        self.assertTrue(PROTECTED_CLASS_CODES.get(self.protected_example.protected_class) in self.content)

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


class Complaint_Show_View_Test(TestCase):
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


class SectionAssignmentTests(TestCase):
    def test_voting_primary_complaint(self):
        # Unless a protected class of disability is selected, reports
        # with a primary complaint of voting should be assigned to voting.
        SAMPLE_REPORT['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**SAMPLE_REPORT)
        test_report.save()
        self.assertTrue(test_report.assign_section() == 'VOT')

    def test_voting_disability_exception(self):
        # Reports with a primary complaint of voting and protected class of disability
        # should not be assigned to voting.
        SAMPLE_REPORT['primary_complaint'] = 'voting'
        test_report = Report.objects.create(**SAMPLE_REPORT)
        disability = ProtectedClass.objects.get_or_create(protected_class='Disability (including temporary or recovery)')
        test_report.protected_class.add(disability[0])
        test_report.save()
        self.assertFalse(test_report.assign_section() == 'VOT')
        self.assertTrue(test_report.assign_section() == 'ADM')


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
        self.assertTrue('Go to page 12.' in content)
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
        vote_index_2 = str(self.response_2).find('VOT')
        self.assertTrue(vote_index_1 > vote_index_2)

    def test_bad_sort_param(self):
        url_base = reverse('crt_forms:crt-forms-index')
        url_3 = f'{url_base}?sort=-assigned_section'
        response_3 = self.client.get(url_3)
        self.assertTrue(response_3.status_code, '404')


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

class ContactValidationTests(TestCase):
    def test_non_ascii_name(self):
        form = Contact(data={
            'contact_first_name': '李王',
            'contact_last_name': '王-Núñez',
            'contact_email': '',
            'contact_phone': ''
        })
        self.assertTrue(form.is_valid())

    def test_non_ascii_email(self):
        form = Contact(data={
            'contact_first_name': '',
            'contact_last_name': '',
            'contact_email': 'foo@bär.com',
            'contact_phone': ''
        })
        self.assertTrue(form.is_valid())

    def test_invalid_phone(self):
        form = Contact(data={
            'contact_first_name': '',
            'contact_last_name': '',
            'contact_email': 'foo@bär.com',
            'contact_phone': '33333333333333333333333333'
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
        self.assertRedirects(response, '/accounts/login/?next=/form/view')

    def test_view_report_details_authenticated(self):
        self.client.login(username='DELETE_USER', password=self.test_pass)
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_report_details_unauthenticated(self):
        response = self.client.get(reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id}))
        expected_response = '/accounts/login/?next=/form/%s/' % self.report.id
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_response)

    def test_view_all_incorrect_password(self):
        """Attempt with incorrect password redirects to login page."""
        self.client.login(username='DELETE_USER', password='incorrect_password')  # nosec -- this code runs in test only
        response = self.client.get(reverse('crt_forms:crt-forms-index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/form/view')

    def test_required_user_logging(self):
        """For compliance and good forensics, check a sample of required logging events"""
        with LogCapture() as cm:
            self.client = Client()
            self.test_pass = secrets.token_hex(32)
            self.user2 = User.objects.create_user('DELETE_USER_2', 'mccartney@thebeatles.com', self.test_pass)
            self.user2.delete()

            self.assertEqual(
                cm.check_present(
                    ('cts_forms.signals', 'INFO', 'ADMIN ACTION by: CLI CLI @ CLI User saved: 3 permissions: <QuerySet []> staff: False superuser: False active: True'),
                ),
                None,
            )

            self.assertEqual(
                cm.check_present(
                    ('cts_forms.signals', 'INFO', 'ADMIN ACTION by: CLI CLI @ CLI User deleted: 3 permissions: <QuerySet []> staff: False superuser: False active: True'),
                ),
                None,
            )
