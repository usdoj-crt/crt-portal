# used by cloud.gov
web: cd crt_portal && gulp build-sass && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn crt_portal.wsgi --workers 2