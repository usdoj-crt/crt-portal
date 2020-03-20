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


SAMPLE_REPORT = {
    'other_class': "test other",
    'contact_first_name': random.choice(TEST_NAMES),
    'contact_last_name': random.choice(TEST_NAMES),
    'contact_email': fake.ascii_email(),
    'contact_phone': fake.phone_number(),
    'violation_summary': fake.text(),
    'last_incident_month': random.choice(range(1, 12)),
    'last_incident_year': random.choice(range(2017, 2019)),
    'location_name': random.choice(TEST_NAMES),
    'location_city_town': random.choice(TEST_NAMES),
    'location_state': random.choice(STATES),
    'contact_address_line_1': fake.street_address(),
    'contact_address_line_2': fake.secondary_address(),
    'contact_city': random.choice(TEST_NAMES),
    'contact_state': random.choice(STATES),
    'contact_zip': fake.zipcode(),
    'servicemember': 'no',
    'primary_complaint': 'police',
    'location_address_line_1': fake.street_address(),
    'location_address_line_2': fake.secondary_address(),
    'election_details': 'federal',
    'inside_correctional_facility': 'inside',
    'correctional_facility_type': 'state_local',
    'commercial_or_public_place': 'place_of_worship',
    'other_commercial_or_public_place': 'a castle',
    'public_or_private_school': 'private',
    'last_incident_year': 2020,
    'last_incident_day': 31,
    'last_incident_month': 1,
    'crt_reciept_year': 2020,
    'crt_reciept_day': 2,
    'crt_reciept_month': 2,
    'intake_format': 'phone',
}