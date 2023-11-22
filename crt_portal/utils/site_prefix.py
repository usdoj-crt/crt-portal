import os


def get_site_prefix(for_intake: bool):
    environment = os.environ.get('ENV', 'UNDEFINED')
    production_url = ('https://crt-portal-django-prod.app.cloud.gov'
                      if for_intake
                      else 'https://civilrights.justice.gov')
    return {
        'PRODUCTION': production_url,
        'STAGE': 'https://crt-portal-django-stage.app.cloud.gov',
        'DEVELOP': 'https://crt-portal-django-dev.app.cloud.gov',
    }.get(environment, 'http://localhost:8000')
