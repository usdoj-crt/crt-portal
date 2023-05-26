import urllib.parse


def disable_javascript(page, base_url):
    """Creates a new page with javascript disabled."""
    scheme, location, path, _, _ = urllib.parse.urlsplit(page.url)
    context = page.context.browser.new_context(
        storage_state=page.context.storage_state(),
        java_script_enabled=False,
        base_url=base_url,
    )

    return context.new_page()


def click_button(locatable, text):
    """Clicks the button with the given text label."""
    locators = [
        locator for locator in
        locatable.locator('input,button,a', has_text=text).all()
        if locator.is_visible()
    ]
    if len(locators) == 0:
        raise ValueError(f"Could not find button with text '{text}'")
    if len(locators) > 1:
        raise ValueError(f"Found more than one button with text '{text}'")
    return locators[0].click()


def next_step(page):
    with page.expect_navigation() as response:
        click_button(page, "Next")
    return response.value


def fill_public_form(page, contact_email="testing@test.com"):
    """Fills the form out to submission."""
    page.goto("/report")
    assert page.title() == "Step 1: Contact - Contact the Civil Rights Division | Department of Justice"

    # Fill input[name="0-contact_first_name"]
    page.fill("input[name='0-contact_first_name']", "Testing")

    # Fill input[name="0-contact_last_name"]
    page.fill("input[name='0-contact_last_name']", "Tester")

    # Fill input[name="0-contact_email"]
    page.fill("input[name='0-contact_email']", contact_email)

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
    next_step(page)
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"

    # Check voting
    page.check("#id_1-primary_complaint_4")

    # Check footer exist
    content = page.text_content("footer")

    assert "Links" in content

    # Check privacy footer
    assert "Privacy Policy" in content

    # Go to step 3
    next_step(page)
    assert page.title() == "Step 3: Location - Contact the Civil Rights Division | Department of Justice"

    # Fill input[name="2-location_name"]
    page.fill("input[name='2-location_name']", "Test store")

    # Fill input[name="2-location_city_town"]
    page.fill("input[name='2-location_city_town']", "Testing")

    # Select Alabama
    page.select_option('select#id_2-location_state', 'AL')

    # Go to step 4
    next_step(page)
    assert page.title() == "Step 4: Personal characteristics - Contact the Civil Rights Division | Department of Justice"

    # Check AGE
    page.check("#id_8-protected_class_0")

    # Go to step 5
    next_step(page)
    assert page.title() == "Step 5: Date - Contact the Civil Rights Division | Department of Justice"

    # Fill input[name="10-last_incident_month"]
    page.fill("input[name='9-last_incident_month']", "1")

    # Fill input[name="10-last_incident_year"]
    page.fill("input[name='9-last_incident_year']", "2020")

    # Go to step 6
    next_step(page)
    assert page.title() == "Step 6: Personal description - Contact the Civil Rights Division | Department of Justice"

    # Fill textarea[name="11-violation_summary"]
    page.fill("textarea[name='10-violation_summary']", "Test report submission")

    # Go to step 7
    next_step(page)
    assert page.title() == "Step 7: Review - Contact the Civil Rights Division | Department of Justice"
