"""
This test serves two purposes:
- It clicks through all of the walkthroughs and ensures there's no errors.
- It produces a PDF of the walkthroughs for users who prefer to read them.
"""
import logging
import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, element


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_walkthroughs(page):
    logging.basicConfig(level=logging.INFO)
    login_as_superuser(page)

    example_tour = page.locator('#content-main .tours tr[data-tour="example"] th .start-tour')
    assert element.normalize_text(example_tour) == 'Example walkthrough'

    all_tours = [
        tour.get_attribute('data-tour')
        for tour
        in page.locator('#content-main .tours tr').all()
    ]

    logging.warning(f'Discovered walkthroughs: {all_tours}')

    for tour in all_tours:
        page.goto('/admin/')
        _click_through_steps(page, tour)


def _click_through_steps(page, tour, *, current_step=None, total_steps=None):
    if current_step is None:
        page.click(f'#content-main .tours tr[data-tour="{tour}"] th .start-tour')
        page.wait_for_selector('.shepherd-text')

        current_step, total_steps = [
            int(step.strip())
            for step
            in page.locator('.shepherd-step-count').inner_text().split('/')
        ]

    step = page.locator(f'.shepherd-step-number-{current_step}')
    step.wait_for()

    logging.warning(f'Clicking through walkthrough {tour} ({current_step}/{total_steps})')
    if current_step < total_steps:
        step.locator('.shepherd-button').filter(has_text="Next").click()
        return _click_through_steps(page, tour, current_step=current_step + 1, total_steps=total_steps)

    step.locator('.shepherd-button').filter(has_text="Done").click()
