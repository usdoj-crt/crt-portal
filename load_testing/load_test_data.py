import random

from faker import Faker
fake = Faker()

# can't use lazy translated strings outside of django
SECTIONS = ['ADM', 'APP', 'CRM', 'DRS', 'ELS', 'EOS', 'FCS', 'HCE', 'IER', 'SPL', 'VOT']
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


SAMPLE_PRO_FORM = {
    'pro_form_view-current_step': 0,
    '0-other_class': "test other",
    '0-contact_first_name': random.choice(TEST_NAMES),
    '0-contact_last_name': random.choice(TEST_NAMES),
    '0-contact_email': fake.ascii_email(),
    '0-contact_phone': fake.phone_number(),
    '0-violation_summary': fake.text(),
    '0-last_incident_month': random.choice(range(1, 12)),
    '0-last_incident_year': random.choice(range(2017, 2019)),
    '0-location_name': random.choice(TEST_NAMES),
    '0-location_city_town': random.choice(TEST_NAMES),
    '0-location_state': random.choice(STATES),
    '0-contact_address_line_1': fake.street_address(),
    '0-contact_address_line_2': fake.secondary_address(),
    '0-contact_city': random.choice(TEST_NAMES),
    '0-contact_state': random.choice(STATES),
    '0-contact_zip': fake.zipcode(),
    '0-servicemember': 'no',
    '0-primary_complaint': 'police',
    '0-location_address_line_1': fake.street_address(),
    '0-location_address_line_2': fake.secondary_address(),
    '0-election_details': 'federal',
    '0-inside_correctional_facility': 'inside',
    '0-correctional_facility_type': 'state_local',
    '0-commercial_or_public_place': 'place_of_worship',
    '0-other_commercial_or_public_place': 'a castle',
    '0-public_or_private_school': 'private',
    '0-last_incident_year': 2020,
    '0-last_incident_day': 31,
    '0-last_incident_month': 1,
    '0-crt_reciept_year': 2020,
    '0-crt_reciept_day': 2,
    '0-crt_reciept_month': 2,
    '0-intake_format': 'phone',
}
