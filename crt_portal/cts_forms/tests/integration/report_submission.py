from playwright import sync_playwright


TARGET = "http://localhost:8000"


def run(browser):
    """
    Complete entire Report submission workflow
    filling all required fields with valid input
    and not editing on review step
    """
    context = browser.newContext()

    # Open new page
    page = context.newPage()
    live_server_url = TARGET
    page.goto(f'{live_server_url}/#report-a-violation')
    # Click text="Start a report"
    page.click("text=\"Start a report\"")
    assert page.url == f'{live_server_url}/#report-a-violation'

    # Click text="Submit a report"
    page.click("text=\"Submit a report\"")
    assert page.url == f'{live_server_url}/report/'
    assert page.title() == "Step 1: Contact - Contact the Civil Rights Division | Department of Justice"

    # Click input[name="0-contact_first_name"]
    page.click("input[name=\"0-contact_first_name\"]")

    # Fill input[name="0-contact_first_name"]
    page.fill("input[name=\"0-contact_first_name\"]", "Joe")

    # Press Tab
    page.press("input[name=\"0-contact_first_name\"]", "Tab")

    # Fill input[name="0-contact_last_name"]
    page.fill("input[name=\"0-contact_last_name\"]", "K")

    # Press Tab
    page.press("input[name=\"0-contact_last_name\"]", "Tab")

    # Fill input[name="0-contact_email"]
    page.fill("input[name=\"0-contact_email\"]", "testing")

    # Click input[name="0-contact_email"]
    page.click("input[name=\"0-contact_email\"]")

    # Fill input[name="0-contact_email"]
    page.fill("input[name=\"0-contact_email\"]", "testing@test.edu")

    # Click input[name="0-contact_phone"]
    page.click("input[name=\"0-contact_phone\"]")

    # Fill input[name="0-contact_phone"]
    page.fill("input[name=\"0-contact_phone\"]", "555-555-5555")

    # Click input[name="0-contact_address_line_1"]
    page.click("input[name=\"0-contact_address_line_1\"]")

    # Fill input[name="0-contact_address_line_1"]
    page.fill("input[name=\"0-contact_address_line_1\"]", "1 tester street")

    # Click input[name="0-contact_city"]
    page.click("input[name=\"0-contact_city\"]")

    # Fill input[name="0-contact_city"]
    page.fill("input[name=\"0-contact_city\"]", "Testing")

    # Press Tab
    page.press("input[name=\"0-contact_city\"]", "Tab")

    # Fill input[name="0-contact_zip"]
    page.fill("input[name=\"0-contact_zip\"]", "10001")

    # Fill input[name="0-servicemember"]
    page.check("input[name=\"0-servicemember\"]")

    # Go to https://crt-portal-django-dev.app.cloud.gov/report/
    page.click("#submit-next")

    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"
    # Check voting
    page.check("#id_1-primary_complaint_0")

    # Click ul[role="presentation"]
    page.click("ul[role=\"presentation\"]")

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"

    # Check NOT hatecrime
    page.check("//li[normalize-space(.)='No']/input[normalize-space(@type)='radio' and normalize-space(@name)='2-hate_crime']")

    # Click //label[normalize-space(.)='No']
    page.click("//label[normalize-space(.)='No']")

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 3: Location - Contact the Civil Rights Division | Department of Justice"

    # Click input[name="3-location_name"]
    page.click("input[name=\"3-location_name\"]")

    # Fill input[name="3-location_name"]
    page.fill("input[name=\"3-location_name\"]", "Test store")

    # Click input[name="3-location_city_town"]
    page.click("input[name=\"3-location_city_town\"]")

    # Fill input[name="3-location_city_town"]
    page.fill("input[name=\"3-location_city_town\"]", "Testing")

    # Select Alabama
    page.selectOption('select#id_3-location_state', 'AL')

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 4: Personal characteristics - Contact the Civil Rights Division | Department of Justice"

    # Check AGE
    page.check("#id_9-protected_class_0")

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 5: Date - Contact the Civil Rights Division | Department of Justice"

    # Click input[name="10-last_incident_month"]
    page.click("input[name=\"10-last_incident_month\"]")

    # Fill input[name="10-last_incident_month"]
    page.fill("input[name=\"10-last_incident_month\"]", "1")

    # Press Tab
    page.press("input[name=\"10-last_incident_month\"]", "Tab")

    # Press Tab
    page.press("input[name=\"10-last_incident_day\"]", "Tab")

    # Fill input[name="10-last_incident_year"]
    page.fill("input[name=\"10-last_incident_year\"]", "2020")

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 6: Personal description - Contact the Civil Rights Division | Department of Justice"

    # Click textarea[name="11-violation_summary"]
    page.click("textarea[name=\"11-violation_summary\"]")

    # Fill textarea[name="11-violation_summary"]
    page.fill("textarea[name=\"11-violation_summary\"]", "Test report submission")

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Step 7: Review - Contact the Civil Rights Division | Department of Justice"

    # Click input[type="submit"]
    page.click("input[type=\"submit\"]")
    assert page.title() == "Contact the Civil Rights Division | Department of Justice"


with sync_playwright() as p:
    for browser_type in [p.chromium]:
        browser = browser_type.launch()
        run(browser)
        browser.close()
