import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console


def toggle_feature_for_user(*,
                            page,
                            feature_name: str,
                            username: str,
                            enable: bool):
    page.goto("/admin/features/feature/")

    team_management_link = next(
        result.locator('.field-pk a')
        for result in page.locator('#result_list tbody tr').all()
        if feature_name in result.locator('.field-name').text_content()
    )

    with page.expect_navigation():
        team_management_link.click()

    if page.locator("input[name='enabled']").is_checked():
        page.check("input[name='enabled']")

    option = page.locator(f'option[title="{username}"]')
    add_link = page.locator("#id_users_when_disabled_add_link")
    remove_link = page.locator("#id_users_when_disabled_remove_link")

    option.click()
    if enable:
        add_link.click()

    if not enable:
        remove_link.click()

    with page.expect_navigation():
        page.click("input[type='submit']")


@pytest.mark.only_browser("chromium")
@console.raise_errors()
def test_can_enable_features_per_user(page):
    """Filters and takes action on an open report."""
    username = login_as_superuser(page)

    toggle_feature_for_user(page=page,
                            feature_name='team-management-redo',
                            username=username,
                            enable=False)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 2

    toggle_feature_for_user(page=page,
                            feature_name='team-management-redo',
                            username=username,
                            enable=True)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 3
    assert '🆕 Team Management' in nav[2].text_content().strip()

    toggle_feature_for_user(page=page,
                            feature_name='team-management-redo',
                            username=username,
                            enable=False)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 2
