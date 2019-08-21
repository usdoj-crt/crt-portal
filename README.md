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

Also note, that the staticfiles folder is the destination of all static assets when you or a script runs `manage.py collectstatic` so don't make your changes there, or they will be overwritten.

## cloud.gov set up
You only need to get the services stood up, configure the S3 bucket once.

For working with cloud.gov directly, you will need to [install the cloud foundry cli](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html). That will allow you ro run the `cf` commands in a terminal.

Log on with `cf login -a api.fr.cloud.gov --sso` and go to the link to sign in and get your pass-code.

### Initial cloud.gov set up
First log into the desired space.

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

(or basic-sandbox if in sandbox)


- store environment variables
 cf cups VCAP_SERVICES -p SECRET_KEY

when prompted give it the secret key


You will needed to enable CORS via awscli, instructions are here: https://cloud.gov/docs/services/s3/#allowing-client-side-web-access-from-external-applications


Right now, the route is set for the production space, we will want to pass in different routes for different spaces but that can be handled when we add the automation.

To deploy run:

    cf push

That will push to cloud.gov according to the instructions in the manifest and Profile.

### Create admin accounts

Need to ssh to create superuser (would like to do this automatically in another PR)

    cf ssh crt-portal-django

Once in, activate local env

    /tmp/lifecycle/shell

Then, you can create a superuser

    python /crt_portal/manage.py createsuperuser

### Subsequent deploys

Once cloud.gov is set up, you can deploy just with a push

    cf push

# Background notes

These are some technologies we are using in the build, here are some links for background.

Pipenv
This is what we use to manage python packages

- https://github.com/pypa/pipenv

Postgres
Here are the database docs
- https://www.postgresql.org/download/

This is a tool for for interfacing with postgres [pgcli](https://www.pgcli.com/)

Docker
We are using containers for local development.

- https://wsvincent.com/django-docker-postgresql/

USWDS
We are using 2.0 as our base
- https://designsystem.digital.gov/

Django
This is the web framework
- https://docs.djangoproject.com/en/2.2/

Cloud.gov
This is the PaaS the app is on
- https://cloud.gov/docs/
