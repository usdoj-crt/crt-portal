import random

from faker import Faker
fake = Faker()

# can't use lazy translated strings outside of django
SECTIONS = ['ADM', 'APP', 'CRM', 'DRS', 'ELS', 'EOS', 'FCS', 'HCE', 'IER', 'POL', 'SPL', 'VOT']
STATUSES = ['new', 'open', 'closed']
STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]
#  seeding these so that the test data will feed the query tests
TEST_NAMES = ['Liam', 'Charlotte', 'Oliver', 'Amelia', 'Emilia', 'Theodore', 'Violet', 'Declan', 'Aria']


def random_form(step, index, csrftoken, form):
    data = [
        {
            '0-contact_first_name': random.choice(TEST_NAMES),
            '0-contact_last_name': random.choice(TEST_NAMES),
            '0-contact_email': fake.ascii_email(),
            '0-contact_phone': fake.phone_number(),
            '0-contact_address_line_1': fake.street_address(),
            '0-contact_address_line_2': fake.secondary_address(),
            '0-contact_city': random.choice(TEST_NAMES),
            '0-contact_state': random.choice(STATES),
            '0-contact_zip': fake.zipcode(),
            '0-servicemember': random.choice(['yes', 'no']),
        },
        {
            f'{step}-primary_complaint': 'something_else',
        },
        # ids may be different in different environments
        {
            f'{step}-hatecrimes_trafficking': 1,
            f'{step}-hatecrimes_trafficking': 2,
        },
        {
            f'{step}-location_name': random.choice(TEST_NAMES),
            f'{step}-location_address_line_1': fake.street_address(),
            f'{step}-location_address_line_2': fake.secondary_address(),
            f'{step}-location_name': random.choice(TEST_NAMES),
            f'{step}-location_city_town': random.choice(TEST_NAMES),
            f'{step}-location_state': random.choice(STATES),
        },
        # these ids appear in my local and prod
        {
            f'{step}-protected_class': 16,
            f'{step}-protected_class': 7,
            f'{step}-protected_class': 15,
            f'{step}-protected_class': 6,
            f'{step}-protected_class': 4,
            f'{step}-other_class': random.choice(TEST_NAMES),
        },
        {
            f'{step}-last_incident_year': random.choice([2019, 2018, 2017]),
            f'{step}-last_incident_day': random.choice(range(1, 29)),
            f'{step}-last_incident_month': random.choice(range(1, 12)),
        },
        {
            f'{step}-violation_summary': fake.text(),
        },
        # review page
        {},
    ]

    if form == 'multi-step':
        form = {'crt_report_wizard-current_step': step, 'csrfmiddlewaretoken': csrftoken}
        form.update(data[index])
        return form

    if form == 'pro':
        form = {
            'pro_form_view-current_step': 0,
            'csrfmiddlewaretoken': csrftoken,
            '0-election_details': 'federal',
            '0-inside_correctional_facility': 'inside',
            '0-correctional_facility_type': 'state_local',
            '0-commercial_or_public_place': 'place_of_worship',
            '0-other_commercial_or_public_place': 'a castle',
            '0-public_or_private_school': 'private',
            '0-crt_reciept_day': random.choice(range(1, 28)),
            '0-crt_reciept_month': random.choice(range(1, 12)),
            '0-crt_reciept_year': random.choice([2019, 2018, 2017]),
            '0-intake_format': random.choice(['phone', 'fax', 'email', 'letter']),
        }
        for datum in data:
            form.update(datum)
        return form
