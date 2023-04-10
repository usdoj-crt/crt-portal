# used by cloud.gov
web: cd crt_portal && python manage.py migrate && python manage.py update_response_templates && python manage.py compilemessages && python manage.py collectstatic --noinput && gunicorn crt_portal.wsgi -t 60 --limit-request-line 8190
