SAMPLE_REPORT_1 = {
    "other_class": "test other",
    "contact_first_name": "Lincoln",
    "contact_last_name": "Abraham",
    "contact_email": "Lincoln@usa.gov",
    "contact_phone": "202-867-5309",
    "violation_summary": "Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.",
    "last_incident_month": 1,
    "last_incident_year": 2019,
    "location_name": "Yosemite",
    "location_city_town": "Yosemite Valley",
    "location_state": "CA",
    "language": "en",
    "crt_reciept_day": 1,
    "crt_reciept_month": 12,
    "crt_reciept_year": 2000,
    "intake_format": "web",
    "assigned_section": "ADM"
}

SAMPLE_REPORT_2 = {
    "id": 2,
    "other_class": "test other",
    "contact_first_name": "Abby",
    "contact_last_name": "Cadabby",
    "contact_email": "abby@fake.com",
    "contact_phone": "773-555-5309",
    "violation_summary": "injustice",
    "last_incident_month": 2,
    "last_incident_year": 2022,
    "location_name": "Chicago",
    "location_city_town": "Chicago",
    "location_state": "IL",
    "language": "en",
    "crt_reciept_day": 2,
    "crt_reciept_month": 2,
    "crt_reciept_year": 2022,
    "intake_format": "web",
    "public_id": "2",
    "assigned_section": "CRM"
}

SAMPLE_REPORT_3 = {
    "id": 3,
    "other_class": "testing more stuff",
    "contact_first_name": "Big",
    "contact_last_name": "Bird",
    "contact_email": "bigbird@fake.com",
    "contact_phone": "202-555-5555",
    "create_date": "2022-02-01 18:17:52.74131+00",
    "violation_summary": "civil rights violation",
    "last_incident_month": 1,
    "last_incident_year": 2022,
    "location_name": "Chicago",
    "location_city_town": "Chicago",
    "location_state": "IL",
    "language": "en",
    "crt_reciept_day": 1,
    "crt_reciept_month": 1,
    "crt_reciept_year": 2022,
    "intake_format": "web",
    "assigned_section": "CRM"
}


SAMPLE_REPORT_4 = {
    "id": 4,
    "other_class": "testing testing",
    "contact_first_name": "Bert",
    "contact_last_name": "Muppet",
    "contact_email": "bert@fake.com",
    "contact_phone": "202-555-0000",
    "create_date": "2022-02-04 18:17:52.74131+00",
    "violation_summary": "civil rights violation",
    "last_incident_month": 12,
    "last_incident_year": 2021,
    "location_name": "Chicago",
    "location_city_town": "Chicago",
    "location_state": "IL",
    "language": "en",
    "crt_reciept_day": 1,
    "crt_reciept_month": 1,
    "crt_reciept_year": 2022,
    "intake_format": "web",
    "assigned_section": "CRM"
}

SAMPLE_RESPONSE_TEMPLATE = {
    "title": "test",
    "subject": "test data with record {{ record_locator }}",
    "body": "test template with record {{ record_locator }}",
}

SAMPLE_ACTION_1 = {
    "id": 1,
    "actor_object_id": 1,
    "verb": "Contacted complainant:",
    "description": "Email sent: 'EOS - Department of Ed OCR Referral Form Letter' to cookiemonster@fakeemail.com via govDelivery TMS",
    "timestamp": "2022-04-12 14:56:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "4"
}

SAMPLE_ACTION_2 = {
    "id": 2,
    "actor_object_id": 1,
    "verb": "Contacted complainant:",
    "description": "Email sent: 'EOS - EEOC Referral Form Letter' to    eileenmcfarland@navapbc.com via govDelivery TMS",
    "timestamp": "2022-04-12 17:30:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "2"
}

SAMPLE_ACTION_3 = {
    "id": 3,
    "actor_object_id": 1,
    "verb": "Contacted complainant:",
    "description": "Email sent: 'EOS - EEOC Referral Form Letter' to  bigbird@fake.com via govDelivery TMS",
    "timestamp": "2022-04-15 10:56:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "3"
}

SAMPLE_ACTION_4 = {
    "id": 4,
    "actor_object_id": 1,
    "verb": "Added comment: ",
    "description": "Email sent: 'SPL - Standard Form Letter' to gregory94@example.com via govDelivery TMS",
    "timestamp": "2022-05-01 10:56:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "4"
}

SAMPLE_ACTION_5 = {
    "id": 5,
    "actor_object_id": 1,
    "verb": "Added comment: ",
    "description": "Email sent: 'DRS - EEOC Referral Form Letter' to stephaniegomez@example.com via govDelivery TMS",
    "timestamp": "2022-05-04 10:56:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "9999999"
}

SAMPLE_ACTION_6 = {
    "id": 6,
    "actor_object_id": 1,
    "verb": "Contacted complainant:",
    "description": "Email sent: 'CRT - Request for Agency Review' to hernandezcolleen@example.com via govDelivery TMS",
    "timestamp": "2022-05-04 10:56:53.277142+00",
    "public": True,
    "actor_content_type_id": 1,
    "target_object_id": "1"
}
