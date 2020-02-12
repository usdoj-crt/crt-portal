[![CircleCI](https://circleci.com/gh/usdoj-crt/crt-portal.svg?style=svg)](https://circleci.com/gh/usdoj-crt/crt-portal)

## Contents

* [Local set up](#local-set-up)

* [Running common tasks](#running-common-tasks)

* [Tests](#tests)

* [Cloud.gov set up](#cloudgov-set-up)

* [Deployment](#deployment)

* [Additional documentation](#additional-documentation)

* [Background notes](#background-notes)

## Local set up

Install Docker

    https://www.docker.com/get-started

Create [ssh key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) and add it to GitHub.

Clone the project locally:

    git clone git@github.com:usdoj-crt/crt-portal.git

In the top level directory create a .env file in the top of your directory and set `SECRET_KEY` to a long, random string.

    SECRET_KEY=''

To build the project
    You will need to build the project for the first time and when there are package updates to apply.

    docker-compose up -d --build

To run the project
    This is a quicker way to start the project as long as you don't have new packages to install.

    docker-compose up

Visit the site locally at [http://0.0.0.0:8000/report] 🎉

Create a superuser for local admin access

     docker-compose run web python /code/crt_portal/manage.py createsuperuser

To add some test data with the form http://0.0.0.0:8000/report and then you can check it out in the backend view http://0.0.0.0:8000/form/view and the admin view at http://0.0.0.0:8000/admin.

Generate the SASS for the front end with gulp:

If you are doing front end work, you will want to have gulp compile the css so you can instantly see changes.

To ensure we are all using the same versions of our front-end dependencies, we use `nvm` to peg a version of node to this project.

Check that `nvm` is installed with `nvm --version`.

If not, run the following command to install it:

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.1/install.sh | bash
    source ~/.bash_profile

If you get an error, and don't have a `bash_profile` file, create one first with `touch ~/.bash_profile`, then run the command above again.

Then, if this is your first time installing the project or `nvm`, run `nvm install`.

Finally, `nvm use && npm install`

Now to compile the sass files into css, run:

    npm run sass:watch

Also note, that the staticfiles folder is the destination of all static assets when you or a script runs `manage.py collectstatic` so don't make your changes there, or they will be overwritten.


## Running common tasks

### Migrations

In Django, when you update the data models you need to create migrations and then apply those migrations, you can do that with:

    docker-compose run web python /code/crt_portal/manage.py makemigrations
    docker-compose run web python /code/crt_portal/manage.py migrate

### Installing a new Python package
To install a new Python package, run:

    docker-compose run web pipenv install name-of-package

### SSH'ing into Docker locally

To ssh into your local Docker web container run:

    docker exec -it crt-portal_web_1 /bin/bash

### Logging into Docker database locally

To log into your local Docker database for debugging purposes, first run:

    docker exec -it crt-portal_db_1 /bin/bash

Then from, within the container, you can run:

    psql -U postgres

As a logged-in local Postgres user, you can run queries directly against the database, for example: `select * from cts_forms_report;` to see report data in your local database.

### I18N

Important commands to use during internationalization (i18n):

When you run `makemessages`, Django will search through .py, .txt, and .html files to find strings marked for translation. Django finds these strings through the `gettext` function or its lazy-loading equivalent (in Python) or the `trans` function (in HTML). This adds the marked strings to `.po` files where translators will do their work.

    docker-compose run web django-admin makemessages -l es

After the strings translated, the translation can be compiled back to Django-readable `.mo` files using run `compilemessages`:

    docker-compose run web django-admin compilemessages

### Hard reset with a fresh database

If your local database is in a wonky state, you might want to try tearing it all down and rebuilding from scratch.

First, shut down any containers you have running locally. Then run:

    docker system prune --volumes

The volumes are the data elements in Docker. Note that you will need to re-create any local user roles after running this command, and the database will be in an empty state, with no complaint records.

:warning: Note that this command will prune **all** containers, images, and caches on your local machine -- not just the crt-portal project.

## Tests

Tests run automatically with repos that are integrated with Circle CI. You can run those tests locally with the following instructions.

Run unit test on **Windows**:
1. Ensure docker is running
2. Start a powershell as admin (git bash has issue running ssh console in docker)
3. Find the id for the web container
   ```
    docker container ls
   ```
4. Identify the id for the crt-portal_web_1
5. SSH to web container in docker:
    ```
    docker exec -it [id for the crt-portal_web goes here] /bin/bash (see below)
    docker exec -it 0a6039095e34 /bin/bash
    ```
6. Once you are in the SSH ./code run the test command below:
    ```
    python crt_portal/manage.py test cts_forms
    ```
7. If you lucky your test will result OK or lots of error to work on!


Run unit test on **MAC**:

You can also run project tests using docker with:

    docker-compose run web python /code/crt_portal/manage.py test cts_forms

This will run [tests.py](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/tests.py), where the business logic tests live. It will also run [test_all_section_assignments.py](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/test_all_section_assignments.py), a script that generates a csv in the /data folder that has the relevant permutations of form fields and runs the out put from the (section assignment function)[https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/models.py#L125]. The idea is that we can expand the spreadsheet and the script to check outcomes. Then it will be a true test, in the meantime, this is not being run as part of deploy.

You can also run a subset of tests, for example:

    docker-compose run web python /code/crt_portal/manage.py test cts_forms.tests.Valid_Form_Tests


For accessibility testing with Pa11y, you can run that locally, _if you have npm installed locally_ with:

    npm run test:a11y

You can scan the code for potential python security flaws using [bandit](https://github.com/PyCQA/bandit). Run bandit manually:

    docker-compose run web bandit -r crt_portal/

If there is a false positive you can add `# nosec` at the end of the line that is triggering the error. Please also add a comment that explains why that line is a false positive.

You can check for Python style issues by running flake8:

    docker-compose run web flake8

If you have a a reason why a line of code shouldn't apply flake8 you can add `# noqa`, but try to use that sparingly.

You can check for JS style issues by running Prettier:

    npm run lint:check

Prettier can automatically fix JS style issues for you:

    npm run lint:write

## Browser targeting

We aim to test against Interent Explorer 11 and Google Chrome on a regular basis, and test against Safari and Firefox on an occasional basis.

## cloud.gov set up
You only need to get the services stood up and configure the S3 bucket once.

For working with cloud.gov directly, you will need to [install the cloud foundry cli](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html). That will allow you to run the `cf` commands in a terminal.

First, login to cloud.gov at https://login.fr.cloud.gov/login and then, get a passcode https://login.fr.cloud.gov/passcode.

Log on with `cf login -a api.fr.cloud.gov --sso-passcode <put_passcode_here>`

### Initial cloud.gov set up
First, log into the desired space.

Create postgres DB and S3 with development settings:

    cf create-service aws-rds shared-psql crt-db
    cf create-service s3 basic-public crt-s3

Store environment variables

    cf cups VCAP_SERVICES -p SECRET_KEY

when prompted give it the secret key

You will needed to enable CORS via awscli, for each bucket instructions are here: https://cloud.gov/docs/services/s3/#allowing-client-side-web-access-from-external-applications

Create a [service account for deployment](https://cloud.gov/docs/services/cloud-gov-service-account/) for each space you are setting up. (Replace "SPACE" with the name of the space you are setting up.)

    cf create-service cloud-gov-service-account space-deployer crt-service-account-SPACE
    cf create-service-key crt-service-account-SPACE crt-portal-SPACE-key
    cf service-key crt-service-account-SPACE crt-portal-SPACE-key

Those credentials will need to be added to CircleCI as environment variables: `CRT_USERNAME_SPACE` `CRT_PASSWORD_SPACE` (replace "SPACE" with the relevant space).

Right now, the route is set for the production space, we will want to pass in different routes for different spaces but that can be handled when we add the automation.

To deploy manually, make sure you are logged in, run the push command and pass it the name of the manifest for the space you want to deploy to:

    cf push -f manifest_space.yaml

That will push to cloud.gov according to the instructions in the manifest and Profile.

### User roles and permissions

As of October 2019, we have two user roles in the system:

* __Staff.__ Logged-in staff can view the table of complaints at `/form/view`.

* __Admin (superusers).__ Logged-in admins can add and remove users, adjust form settings such as the list of protected classes, and view the table of complaints at `/form/view`.

Please update the [Accounts Spreadsheet](https://docs.google.com/spreadsheets/d/1VM5hSsxUgqFM6t51Ejm_EjxnbxLI-pTXF_CVxZJSekQ/edit#gid=0) if you create or modify any user accounts.

As we build out the product, we expect to add more granular user roles and permissions.

For production, we use DOJ's Single Sign on for authentication. For the ADFS authentication, you need to make sure that public urls are listed in settings.py in the `AUTH_ADFS` section.

For the dev and staging site, you will want to make sure the `@login_required` decorator are on all views that need authentication.

Setting up single sign on is documented in [docs/maintenance_or_infrequent_tasks](https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#single-sign-on).

### Create and update admin accounts

Need to ssh to create superuser (would like to do this automatically in another PR):

    cf ssh crt-portal-django

Once in, activate local env:

    /tmp/lifecycle/shell

Then, you can create a superuser:

    python crt_portal/manage.py createsuperuser

Or change a user's password:

    python crt_portal/manage.py changepassword {{username}}

## Deployment

We deploy from [CircleCI](https://circleci.com/gh/usdoj-crt). The [circle config](https://github.com/usdoj-crt/crt-portal/blob/develop/.circleci/config.yml) contains rules that will deploy the site to different environments using a set of rules.

[GitFlow](https://github.com/nvie/gitflow) is a tool that can make it easier to handle branching. On a Mac with homebrew it can be installed with: 

    brew install git-flow 
Then, in the top level folder of the project, you will want to run: 
    
    git flow init 
We are using the defaults, so you can press enter for all the set up options. You may need to type 'master' production releases if you haven't been on the master branch yet. 

### Deployment for each environment
* The app will deploy to **dev** when the tests pass and a PR is merged into `develop`. You should do this in GitHub.

* The app will deploy to **stage** when the tests pass and when we make or update a branch that starts with `release/`.
    * Make sure the develop branch is approved for deploy by the product owner
    * Look at ZenHub and see if there is anything in "Dev done" flag that for approval so those issues are in "Ready for UAT" when you make the release
    * Check out the develop branch and do a `git pull origin develop`
    * You can create a release with the command `git flow release start <date-of-planned-relase>`
    * Finally, push the release branch `git push origin release/<date-of-planned-relase>`

* The app will deploy to **prod** when the tests pass and a PR is merged into `master`. You can also do this in GitHub once you confirm approval with the product owner. If there are any merge conflicts, you will want to resolve them on the staging branch first.
    * If have not been any PRs directly to the release branch you can merge in GitHub
    * If there are PRs to the release branch merge with gitflow:
     * Approve the relese on GitHub
     * Check out the release branch and do a `git pull origin release/<name-of-release>`
     * Check out the master branch and do a `git pull origin master`
     * Check out the develop branch and do a `git pull origin develop`
     * Run `git flow release finish`
     * Check out the develop branch and do a `git push origin develop`
     * Once that succedes, check out the master branch do a `git push origin master`

When CircleCI tries to deploy two PRs back-to-back, one of them can fail. In this case, you can restart the failed deploy process by clicking the "Rerun Workflow" button.

**Hot fixes** will be needed when we find urgent bugs or problems with production. This is where git-flow becomes very useful.
To make the fix:
    * Check out the master branch and do a `git pull origin master`
    * Create a branch for your work with `git flow hotfix start`
    * Commit and push your branch for PR review

To deploy the fix:
    * Make sure the product owner is in the loop with any errors and fixes.
    * Approve the hotfix merge on GitHub but don't merge it.
    * Check out the development branch and do a `git pull origin develop`
    * Check out the release branch, if there is one, and do a `git pull origin release/name-of-release`
    * Check out the master branch and do a `git pull origin master`
    * Finish the hotfix with `git flow hotfix finish` This command will make sure that the fix is merged into the master, develop and release branches so your change doesn't get clobbered later.
    * Checkout and push the develop, release and master branches. Checking to make sure the fix works and doesn't cause any unintended consequences.

The [git-flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/) is a great explainer of the git-flow tool.

## Additional documentation

For more technical documentation see the [docs](https://github.com/usdoj-crt/crt-portal/tree/develop/docs)
    - A11y testing plan
    - Branching strategy
    - Maintenance or infrequent tasks
    - Pull request instructions

### Adjust form autocomplete per-instance

To prevent form autocomplete on an application instance, add `FORM_AUTOCOMPLETE_OFF=True` as an environment variable. We are using that in staging to help mask personal data during usability testing.

To restore default behavior of allowing form autocomplete, remove the `FORM_AUTOCOMPLETE_OFF` flag.

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

Thanks for reading all the way!
