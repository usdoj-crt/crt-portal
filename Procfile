# used by cloud.gov
web: cd crt_portal && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn crt_portal.wsgi --workers 2
