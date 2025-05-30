from cts_forms.model_variables import (PRIMARY_COMPLAINT_CHOICES,
                                       SECTION_CHOICES, SERVICEMEMBER_CHOICES,
                                       STATES_AND_TERRITORIES, STATUS_CHOICES,
                                       INTAKE_FORMAT_CHOICES)
from cts_forms.models import Report, Profile
from django.contrib.auth import get_user_model
from tms.models import TMSEmail
from factory import Faker
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from datetime import datetime
from cts_forms.signals import salt
from pytz import timezone

User = get_user_model()


class ReportFactory(DjangoModelFactory):

    class Meta:
        model = Report

    contact_first_name = Faker('first_name')
    contact_last_name = Faker('last_name')
    contact_email = Faker('email', domain="example.com")
    contact_phone = Faker('phone_number')
    contact_address_line_1 = Faker('street_address')
    contact_address_line_2 = Faker('secondary_address')
    contact_state = Faker('state_abbr')
    contact_city = Faker('city')
    contact_zip = Faker('zipcode')

    contact_2_kind = Faker('company')
    contact_2_name = Faker('name')
    contact_2_email = Faker('email', domain="example.com")
    contact_2_phone = Faker('phone_number')
    contact_2_address_line_1 = Faker('street_address')
    contact_2_address_line_2 = Faker('secondary_address')
    contact_2_city = Faker('city')
    contact_2_state = Faker('state_abbr')
    contact_2_zip_code = Faker('zipcode')

    contact_3_kind = Faker('company')
    contact_3_name = Faker('name')
    contact_3_email = Faker('email', domain="example.com")
    contact_3_phone = Faker('phone_number')
    contact_3_address_line_1 = Faker('street_address')
    contact_3_address_line_2 = Faker('secondary_address')
    contact_3_city = Faker('city')
    contact_3_state = Faker('state_abbr')
    contact_3_zip_code = Faker('zipcode')

    contact_4_kind = Faker('company')
    contact_4_name = Faker('name')
    contact_4_email = Faker('email', domain="example.com")
    contact_4_phone = Faker('phone_number')
    contact_4_address_line_1 = Faker('street_address')
    contact_4_address_line_2 = Faker('secondary_address')
    contact_4_city = Faker('city')
    contact_4_state = Faker('state_abbr')
    contact_4_zip_code = Faker('zipcode')

    location_name = Faker('company')
    location_address_line_1 = Faker('street_address')
    location_address_line_2 = Faker('secondary_address')
    location_city_town = Faker('city')
    location_state = FuzzyChoice(STATES_AND_TERRITORIES, getter=lambda c: c[0])

    create_date = Faker('date_this_year')

    violation_summary = Faker('paragraph', nb_sentences=5, variable_nb_sentences=True)

    last_incident_year = Faker('year')
    last_incident_day = Faker('day_of_month')
    last_incident_month = Faker('month')

    primary_complaint = FuzzyChoice(PRIMARY_COMPLAINT_CHOICES, getter=lambda c: c[0])
    servicemember = FuzzyChoice(SERVICEMEMBER_CHOICES, getter=lambda c: c[0])
    status = FuzzyChoice(STATUS_CHOICES, getter=lambda c: c[0])
    assigned_section = FuzzyChoice(SECTION_CHOICES, getter=lambda c: c[0])

    intake_format = FuzzyChoice(INTAKE_FORMAT_CHOICES, getter=lambda c: c[0])


def _create_report():
    report = ReportFactory.build()
    UTC = timezone('UTC')
    report.create_date = UTC.localize(datetime.now())
    # This save creates the report id, report.pk, so we can create a public_id
    report.save()
    salt_chars = salt()
    report.public_id = f'{report.pk}-{salt_chars}'
    report.save()
    return report


class EmailFactory(DjangoModelFactory):

    class Meta:
        model = TMSEmail

    tms_id = Faker('random_int', min=100000000, max=999999999)
    report = _create_report()
    subject = Faker('sentence', nb_words=4)
    body = Faker('paragraph', nb_sentences=5, variable_nb_sentences=True)
    recipient = Faker('email', domain="example.com")
    created_at = Faker('date_this_year')
    completed_at = Faker('date_this_year')
    status = FuzzyChoice(TMSEmail.STATUS_CHOICES, getter=lambda c: c[0])
    purpose = FuzzyChoice(TMSEmail.PURPOSE_CHOICES, getter=lambda c: c[0])
    error_message = ''


class UserFactory():
    class Meta:
        model = User

    def create_user(username, email, password, first_name="", last_name="", has_portal_access=True):
        user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
        user.profile = Profile.objects.create(user=user)
        user.profile.has_portal_access = has_portal_access
        user.profile.save()
        user.save()
        return user
