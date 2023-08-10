import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, features


@pytest.mark.only_browser("chromium")
@console.raise_errors()
def test_can_enable_features_per_user(page):
    """Filters and takes action on an open report."""
    username = login_as_superuser(page)

    features.toggle_feature_for_user(page=page,
                                     feature_name='team-management-redo',
                                     username=username,
                                     enable=False)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 2

    features.toggle_feature_for_user(page=page,
                                     feature_name='team-management-redo',
                                     username=username,
                                     enable=True)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 3
    assert '🆕 Team Management' in nav[2].text_content().strip()

    features.toggle_feature_for_user(page=page,
                                     feature_name='team-management-redo',
                                     username=username,
                                     enable=False)

    page.goto("/form/view")
    nav = page.locator('.usa-nav__primary li').all()
    assert len(nav) == 2
