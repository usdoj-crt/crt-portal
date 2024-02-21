import pytest

from cts_forms.tests.integration_util import console, compat


@pytest.mark.only_browser("chromium")
@console.raise_errors()
def test_select_english_from_banner(page):
    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'

    assert page.is_visible("button[data-value='en']")

    with page.expect_navigation():
        page.click("button[data-value='en']")

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'


@pytest.mark.only_browser("chromium")
@console.raise_errors()
def test_select_spanish_from_banner(page):
    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'

    assert page.is_visible("button[data-value='es']")

    with page.expect_navigation():
        page.click("button[data-value='es']")

    assert page.title() == 'Comuníquese con la División de Derechos Civiles | Departamento de Justicia'


@pytest.mark.only_browser("chromium")
@compat.hide_django_debug_toolbar
@console.raise_errors()
def test_select_english_from_mobile_menu(page):
    page.set_viewport_size({'width': 800, 'height': 1200})

    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'
    assert page.is_visible("button.crt-menu--mobile.usa-menu-btn")

    page.click("button.crt-menu--mobile.usa-menu-btn")

    assert page.is_visible("a[data-value='en']")

    with page.expect_navigation():
        page.click("a[data-value='en']")

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'


@pytest.mark.only_browser("chromium")
@compat.hide_django_debug_toolbar
@console.raise_errors()
def test_select_spanish_from_mobile_menu(page):
    page.set_viewport_size({'width': 800, 'height': 1200})

    page.goto('/')

    assert page.title() == 'Contact the Civil Rights Division | Department of Justice'
    assert page.is_visible("button.crt-menu--mobile.usa-menu-btn")

    page.click("button.crt-menu--mobile.usa-menu-btn")

    assert page.is_visible("a[data-value='es']")

    with page.expect_navigation():
        page.click("a[data-value='es']")

    assert page.title() == 'Comuníquese con la División de Derechos Civiles | Departamento de Justicia'
