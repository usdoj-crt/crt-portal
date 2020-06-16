# used by cloud.gov
web: cd crt_portal && python manage.py migrate && python manage.py compilemessages && python manage.py collectstatic --noinput && newrelic-admin run-program gunicorn crt_portal.wsgi
