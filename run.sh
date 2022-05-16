#!/bin/bash
# used by local docker container

# # make sure migrations are applied
echo Migrating database...
python /code/crt_portal/manage.py migrate


# If LOCALSTACK is set in environment, this will upload static files to the localstack s3 service running in docker
# Otherwise the development server is handling static files
if [[ -n "${USE_LOCALSTACK}" ]]; then

    echo Generating css and js...
    npm run build
    python /code/crt_portal/manage.py collectstatic --noinput

    echo Removing crt-portal s3 bucket
    aws --endpoint-url=${LOCALSTACK_URL} s3 rb s3://crt-portal --force

    echo Creating crt-portal s3 bucket
    aws --endpoint-url=${LOCALSTACK_URL} s3 mb s3://crt-portal

    echo Creating crt-private s3 bucket
    aws --endpoint-url=${LOCALSTACK_URL} s3 mb s3://crt-private

    echo Collecting and uploading static assets to localstack...
    python /code/crt_portal/manage.py collectstatic --noinput
else
  # Since the dev server is handling static files, let's rebuild them as we modify
  echo Watching sass and js to rebuild as we make changes...
  npm start &
  python /code/crt_portal/manage.py collectstatic --noinput
fi;

echo Updating response templates…
python /code/crt_portal/manage.py update_response_templates

echo Compiling i8n files…
python /code/crt_portal/manage.py compilemessages

echo Starting Django Server…
python /code/crt_portal/manage.py runserver 0.0.0.0:8000
