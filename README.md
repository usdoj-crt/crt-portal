## Local set up

Install Docker

    https://www.docker.com/get-started

Create a .env file in the top of your directory and set `SECRET_KEY` to a long, random string.

    SECRET_KEY=''

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


## Running common tasks

In Django, when you update the data models you need to create migrations and then apply those migrations, you can do that with:

    docker-compose run web python /code/crt_portal/manage.py makemigrations
    docker-compose run web python /code/crt_portal/manage.py migrate

To ssh into your local docker container run:

    docker exec -it crt-django_web_1 /bin/bash

To install a new python package run:

    docker-compose run web pipenv install name-of-package

## Tests


Tests run automatically with repos that are integrated with Circle CI. You can run those tests locally with the following instructions.


You can also run project tests using docker with:

    docker-compose run web python /code/crt_portal/manage.py test cts_forms

For accessibility testing with Pa11y, you can run that locally, _if you have npm installed locally_ with:

    npm run test:a11y


You can scan the code for potential python security flaws using [bandit](https://github.com/PyCQA/bandit). Run bandit manually:

    docker-compose run web bandit -r crt_portal/

If there is a false positive you can add `# nosec` at the end of the line that is triggering the error. Please also add a comment that explains why that line is a false positive.

You can check for style issues by running flake8:

    docker-compose run web flake8

If you have a a reason why a line of code shouldn't apply flake8 you can add `# noqa`, but try to use that sparingly.

## cloud.gov set up
You only need to get the services stood up and configure the S3 bucket once.

For working with cloud.gov directly, you will need to [install the cloud foundry cli](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html). That will allow you to run the `cf` commands in a terminal.

Log on with `cf login -a api.fr.cloud.gov --sso` and go to the link to sign in and get your pass-code.

### Initial cloud.gov set up
First, log into the desired space.

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

(or basic-sandbox if in sandbox)


- store environment variables
 cf cups VCAP_SERVICES -p SECRET_KEY

when prompted give it the secret key


You will needed to enable CORS via awscli, for each bucket instructions are here: https://cloud.gov/docs/services/s3/#allowing-client-side-web-access-from-external-applications


Create a [service account for deployment](https://cloud.gov/docs/services/cloud-gov-service-account/) for each space you are setting up. (Replace "space" with the name of the space you are setting up.)

    cf create-service cloud-gov-service-account space-deployer crt-service-account-space
    cf create-service-key crt-service-account-space crt-portal-space-key
    cf service-key crt-service-account-space crt-portal-space-key

Those credentials will need to be added to CircleCI as environment variables: `CRT_USERNAME_SPACE` `CRT_PASSWORD_SPACE` (replace "SPACE" with the relevant space).

Right now, the route is set for the production space, we will want to pass in different routes for different spaces but that can be handled when we add the automation.

To deploy manually, make sure you are logged in, run the push command and pass it the name of the manifest for the space you want to deploy to:

    cf push -f manifest_space.yml

That will push to cloud.gov according to the instructions in the manifest and Profile.

### Create admin accounts

Need to ssh to create superuser (would like to do this automatically in another PR)

    cf ssh crt-portal-django

Once in, activate local env

    /tmp/lifecycle/shell

Then, you can create a superuser

    python /crt_portal/manage.py createsuperuser

### Subsequent deploys

Deploys will happen via Circle CI.
    - For deploys to dev, it will deploy after tests pass, when a PR is merged into the develop branch.
    - For deploys to staging, it will deploy after tests pass, when we make or update a branch the starts with "release/".
    - Once we are cleared to deploy to prod, it will deploy after tests pass, when we merge the release into the master branch.

As a back up contingency, you can deploy just with a push using the manifest:

    cf push -f manifest_space.yml

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
