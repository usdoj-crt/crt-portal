
import pytest


@pytest.mark.only_browser("chromium")
def test_report_complete_and_valid_submission(page):

    def next_step():
        with page.expect_navigation():
            page.click('input[type="submit"]')

    page.goto("/report")
    assert page.title() == "Step 1: Contact - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Fill input[name="0-contact_first_name"]
    page.fill("input[name='0-contact_first_name']", "Testing")

    # Fill input[name="0-contact_last_name"]
    page.fill("input[name='0-contact_last_name']", "Tester")

    # Fill input[name="0-contact_email"]
    page.fill("input[name='0-contact_email']", "testing")

    # Fill input[name="0-contact_email"]
    page.fill("input[name='0-contact_email']", "testing@test.test")

    # Fill input[name="0-contact_phone"]
    page.fill("input[name='0-contact_phone']", "555-555-5555")

    # Fill input[name="0-contact_address_line_1"]
    page.fill("input[name='0-contact_address_line_1']", "1 tester street")

    # Fill input[name="0-contact_city"]
    page.fill("input[name='0-contact_city']", "Testing")

    # Fill input[name="0-contact_zip"]
    page.fill("input[name='0-contact_zip']", "10001")

    # Fill input[name="0-servicemember"]
    page.check("input[name='0-servicemember']")

    # Go to step 2
    next_step()
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Check voting
    page.check("#id_1-primary_complaint_0")

    # Go to step 2-2
    next_step()
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Check NOT hatecrime
    page.check("#id_2-hate_crime_1")

    # Go to step 3
    next_step()
    assert page.title() == "Step 3: Location - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Fill input[name="3-location_name"]
    page.fill("input[name='3-location_name']", "Test store")

    # Fill input[name="3-location_city_town"]
    page.fill("input[name='3-location_city_town']", "Testing")

    # Select Alabama
    page.selectOption('select#id_3-location_state', 'AL')

    # Go to step 4
    next_step()
    assert page.title() == "Step 4: Personal characteristics - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Check AGE
    page.check("#id_9-protected_class_0")

    # Go to step 5
    next_step()
    assert page.title() == "Step 5: Date - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Fill input[name="10-last_incident_month"]
    page.fill("input[name='10-last_incident_month']", "1")

    # Fill input[name="10-last_incident_year"]
    page.fill("input[name='10-last_incident_year']", "2020")

    # Go to step 6
    next_step()
    assert page.title() == "Step 6: Personal description - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Fill textarea[name="11-violation_summary"]
    page.fill("textarea[name='11-violation_summary']", "Test report submission")

    # Go to step 7
    next_step()
    assert page.title() == "Step 7: Review - Contact the Civil Rights Division | Department of Justice"  # nosec

    # Complete submission
    next_step()
    assert page.title() == "Contact the Civil Rights Division | Department of Justice"  # nosec
