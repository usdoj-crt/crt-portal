from cts_forms.model_variables import (PRIMARY_COMPLAINT_CHOICES,
                                       SECTION_CHOICES, SERVICEMEMBER_CHOICES,
                                       STATES_AND_TERRITORIES, STATUS_CHOICES,
                                       INTAKE_FORMAT_CHOICES)
from cts_forms.models import Report
from factory import Faker
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice


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
