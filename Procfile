# used by cloud.gov - see: https://docs.cloudfoundry.org/devguide/deploy-apps/manifest-attributes.html
web: cd crt_portal && python manage.py migrate && python manage.py update_response_templates && python manage.py update_ipynb_examples && python manage.py compilemessages && python manage.py collectstatic --noinput && gunicorn crt_portal.wsgi -t 60 --limit-request-line 8190
