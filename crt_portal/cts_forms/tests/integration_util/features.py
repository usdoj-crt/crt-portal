from typing import List, Union
import functools

from cts_forms.tests.integration_authed.auth import get_test_credentials, login_as_superuser


def login_as_superuser_with_feature(feature_name: str):
    return _toggle_as_superuser(feature_name, True)


def login_as_superuser_without_feature(feature_name: str):
    return _toggle_as_superuser(feature_name, False)


def _toggle_as_superuser(feature_name: str, enabled: bool):
    def wrapper(func):
        @functools.wraps(func)
        def decorator(page, *args, **kwargs):
            login_as_superuser(page)
            username, _ = get_test_credentials()
            toggle_feature_for_user(page=page, feature_name=feature_name, username=username, enable=enabled)
            return func(page, *args, **kwargs)
        return decorator
    return wrapper


def toggle_feature_for_user(*,
                            page,
                            feature_name: Union[str, List[str]],
                            username: str,
                            enable: bool):
    """Toggles a feature for a user.

    If you want one feature toggled for the entire test, see
    superuser_with_feature and superuser_without_feature.
    """
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

    # In Django 5.2, we need to select the option in the correct box before clicking the button
    from_box = page.locator("#id_users_when_disabled_from")
    to_box = page.locator("#id_users_when_disabled_to")
    add_button = page.locator("#id_users_when_disabled_add")
    remove_button = page.locator("#id_users_when_disabled_remove")

    # Check which box contains the user
    from_options = from_box.locator(f'option[title="{username}"]')
    to_options = to_box.locator(f'option[title="{username}"]')

    if enable:
        # Need to move user from "available" to "chosen"
        if from_options.count() > 0:
            from_options.click()
            add_button.click()
    else:
        # Need to move user from "chosen" to "available"
        if to_options.count() > 0:
            to_options.click()
            remove_button.click()

    with page.expect_navigation():
        page.click("input[type='submit']")
