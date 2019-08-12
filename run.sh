#!/bin/bash
# make sure migrations are applied
echo migrate database...
python /code/crt_portal/manage.py migrate

echo Starting Django Server…
python /code/crt_portal/manage.py compress
python /code/crt_portal/manage.py runserver 0.0.0.0:8000
