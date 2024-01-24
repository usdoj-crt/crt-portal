#!/bin/bash
# used by local docker container

# # make sure migrations are applied
echo 'Migrating database...'
python /code/crt_portal/manage.py migrate
python /code/crt_portal/manage.py refresh_form_letters_sent_view

echo 'Generating css and js...'
node node_modules/gulp/bin/gulp build-css
node node_modules/gulp/bin/gulp build-js

echo 'Start `npm run gulp:watch` to recompile assets.'

echo 'Updating response templates…'
python /code/crt_portal/manage.py update_response_templates

echo 'Updating Jupyter Notebooks…'
python /code/crt_portal/manage.py update_ipynb_examples

echo 'Compiling i8n files…'
python /code/crt_portal/manage.py compilemessages

echo 'Starting Django Server…'
python /code/crt_portal/manage.py runserver 0.0.0.0:8000
