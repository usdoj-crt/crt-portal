#!/bin/bash
# used by local docker container

# make sure migrations are applied
echo migrate database...
python /code/crt_portal/manage.py migrate

echo generate css...
npm install
node node_modules/gulp/bin/gulp build-sass

echo collect static assets...
python /code/crt_portal/manage.py collectstatic --noinput

echo Compiling i8n files…
python /code/crt_portal/manage.py compilemessages

echo Starting Django Server…
python /code/crt_portal/manage.py compress
python /code/crt_portal/manage.py runserver 0.0.0.0:8000
