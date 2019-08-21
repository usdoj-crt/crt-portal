## Local set up

Install Docker

    https://www.docker.com/get-started


You can make your own long, random string for your secret key and save it in your local environment or one will be crated for you each time you spin up the project.

    export SECRET_KEY=''

To build the project

    docker-compose up -d --build

To run the project

    docker-compose up


create a superuser for admin access

     docker-compose run web python /code/crt_portal/manage.py createsuperuser


To add some test data after you log in at `http://0.0.0.0:8000/admin/login`; Then you can check out `http://0.0.0.0:8000/form/`.


in another terminal if you are doing front end work:

    gulp watch

## Running common tasks

When running migrations, make sure you set up a SECRET_KEY in a .env file for yourself locally

In Django, when you update the data models you need to create migrations and then apply those migrations, you can do that with:

    docker-compose run web python /code/crt_portal/manage.py makemigrations
    docker-compose run web python /code/crt_portal/manage.py migrate

To ssh into your local docker container run:

    docker exec -it crt-django_web_1 /bin/bash


## cloud.gov set up

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

(or basic-sandbox if in sandbox)


- store environment variables
 cf cups VCAP_SERVICES -p "{'SECRET_KEY': 'replace-with-your-secret-key'}"

(I had to give it the varable name in this command and follow up with the secret key, I am not sure why)

Need to ssh to create superuser (would like to do this automatically in another PR)

    cf ssh crt-portal-django

once in, activate local env

Needed to enable CORS via awscli https://cloud.gov/docs/services/s3/#allowing-client-side-web-access-from-external-applications (would like to do this automatically in another PR)


# Background notes

These are some technologies we are using in the build, here are some links for background.

Pipenv, this is what we use to manage python packages

- https://github.com/pypa/pipenv

Postgres

- https://www.postgresql.org/download/

This is a tool for for interfacing with postgres [pgcli](https://www.pgcli.com/)

Docker
We are using containers for local development.

- https://wsvincent.com/django-docker-postgresql/

USWDS
We are using 2.0 as our base
- https://designsystem.digital.gov/
