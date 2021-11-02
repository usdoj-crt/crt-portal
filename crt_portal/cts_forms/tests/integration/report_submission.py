
import pytest


@pytest.mark.only_browser("chromium")
def test_error_if_form_refreshed(page, base_url):

    def next_step():
        with page.expect_navigation() as response:
            page.evaluate("document.querySelector('input[type=\"submit\"]').click()")
        return response.value

    page.goto("/report")
    # We'll complete the first step
    page.check("input[name='0-servicemember']")
    next_step()

    # Refresh the page in another tab
    new_tab = page.context.new_page()
    new_tab.goto(f"{base_url}/report")

    # Now try and progress on original tab where we're still on step #2
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"
    page.check("#id_1-primary_complaint_0")
    response = next_step()

    # Now we've got an error page on the original tab
    assert response.status == 422
    assert "We're sorry, something went wrong" in response.text()


@pytest.mark.only_browser("chromium")
def test_report_complete_and_valid_submission(page):

    def next_step():
        with page.expect_navigation():
            page.evaluate("document.querySelector('input[type=\"submit\"]').click()")

    page.goto("/report")
    assert page.title() == "Step 1: Contact - Contact the Civil Rights Division | Department of Justice"

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
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"

    # Check voting
    page.check("#id_1-primary_complaint_4")

    # Check footer exist
    content = page.text_content("footer")

    assert "Links" in content

    # Check privacy footer
    assert "Privacy Policy" in content

    # Go to step 3
    next_step()
    assert page.title() == "Step 3: Location - Contact the Civil Rights Division | Department of Justice"

    # Fill input[name="2-location_name"]
    page.fill("input[name='2-location_name']", "Test store")

    # Fill input[name="2-location_city_town"]
    page.fill("input[name='2-location_city_town']", "Testing")

    # Select Alabama
    page.select_option('select#id_2-location_state', 'AL')

    # Go to step 4
    next_step()
    assert page.title() == "Step 4: Personal characteristics - Contact the Civil Rights Division | Department of Justice"

    # Check AGE
    page.check("#id_8-protected_class_0")

    # Go to step 5
    next_step()
    assert page.title() == "Step 5: Date - Contact the Civil Rights Division | Department of Justice"

    # Fill input[name="10-last_incident_month"]
    page.fill("input[name='9-last_incident_month']", "1")

    # Fill input[name="10-last_incident_year"]
    page.fill("input[name='9-last_incident_year']", "2020")

    # Go to step 6
    next_step()
    assert page.title() == "Step 6: Personal description - Contact the Civil Rights Division | Department of Justice"

    # Fill textarea[name="11-violation_summary"]
    page.fill("textarea[name='10-violation_summary']", "Test report submission")

    # Go to step 7
    next_step()
    assert page.title() == "Step 7: Review - Contact the Civil Rights Division | Department of Justice"

    # Click on "Edit this page" for Location
    with page.expect_navigation():
        page.evaluate("document.querySelector('[data-testid=\"edit-location\"] button').click()")
    assert page.title() == "Step 3: Location - Contact the Civil Rights Division | Department of Justice"

    # Navigate back to review page
    next_step()
    next_step()
    next_step()
    next_step()

    # Complete submission
    next_step()
    assert page.title() == "Submission complete"
