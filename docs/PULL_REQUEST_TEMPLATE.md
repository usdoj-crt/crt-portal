[Link to ZenHub issue.](link-goes-here)

## What does this change?

## Screenshots (for front-end PR):

## Checklist:

_these will eventually be enforced by CircleCI; we need to set that up at the USDOJ org level_

+ [ ] If front end or functionality change, run locally and check http://0.0.0.0:8000/report/.
+ [ ] Tests pass locally: `docker-compose run web python /code/crt_portal/manage.py test cts_forms`.
+ [ ] Running `flake8` in root returns no style errors.
+ [ ] pa11y manual check against the `/report` page returns no errors.

## Notes for reviewer:
