import pytest


@pytest.mark.only_browser("chromium")
def test_select_english_from_banner(page):
    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'

    assert page.is_visible("button[data-value='en']")

    with page.expect_navigation():
        page.click("button[data-value='en']")

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'


@pytest.mark.only_browser("chromium")
def test_select_spanish_from_banner(page):
    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'

    assert page.is_visible("button[data-value='es']")

    with page.expect_navigation():
        page.click("button[data-value='es']")

    assert page.title() == 'Comuníquese con la División de Derechos Civiles | Departamento de Justicia'
