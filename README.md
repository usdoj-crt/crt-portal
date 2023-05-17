[![CircleCI](https://circleci.com/gh/usdoj-crt/crt-portal.svg?style=svg)](https://circleci.com/gh/usdoj-crt/crt-portal)
## About the project

This is the code that runs [civilrights.justice.gov](https://civilrights.justice.gov/).

In order to be more responsive to the public’s changing communication needs and the increased reporting volume,the Civil Rights Division, in close collaboration with 18F, launched a user-friendly online submission experience at [civilrights.justice.gov](https://civilrights.justice.gov/). The project has transformed the way the Civil Rights Division collects, sorts, and responds to public reports of civil rights violations.

Here is a [blog post](https://18f.gsa.gov/2020/07/07/transforming-how-dojs-civil-rights-division-engages-with-the-public/) about the launch of this project with more details.

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

In the top level directory create a .env file in the top of your directory and add the following environment variables. Set `SECRET_KEY` to a long, random string and `POSTGRES_PASSWORD`, `POSTGRES_ANALYTICS_PASSWORD`.

    SECRET_KEY="this_is_a_long_random_string"
    POSTGRES_PASSWORD="rando_pw"
    POSTGRES_ANALYTICS_PASSWORD="some_other_password"

To build the project
    You will need to build the project for the first time and when there are package updates to apply.

    docker-compose up -d --build

You can also customize the ports various services run on by specifying the following in your .env file (changing any ports as desired):

```
DATABASE_PORT=5432
WEB_PORT=8000
JUPYTER_PORT=8001
MAILHOG_SMTP_PORT=1025
MAILHOG_UI_PORT=8025
CLAMAV_REST_PORT=9000
LOCALSTACK_PORT=4566
```

To run the project
    This is a quicker way to start the project as long as you don't have new packages to install.

    docker-compose up

You can also build the project under a separate project, detached from local dependencies (ports and volumes) using:

    ./standalone

More configuration for this adanced usage can be found in docker-compose.standalone.yml

Visit the site locally at [http://0.0.0.0:8000/report] 🎉

Create a superuser for local admin access

     docker-compose run web python /code/crt_portal/manage.py createsuperuser

To add some test data with the form http://0.0.0.0:8000/report and then you can check it out in the backend view http://0.0.0.0:8000/form/view and the admin view at http://0.0.0.0:8000/admin.

Generate the SASS and Javascript for the front end with gulp:

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

    npm run gulp:watch

Note that you'll need to turn off localstack for this to work without running `collectstatic`, by setting `USE_LOCALSTACK=False` in `.env`.

Also note, that the staticfiles folder is the destination of all static assets when you or a script runs `manage.py collectstatic` so don't make your changes there, or they will be overwritten.

## Jupyter

### Setting up

There's a few things to set up before Jupyter can be run:

First, be sure you've set up `POSTGRES_ANALYTICS_PASSWORD` (as mentioned above). You'll need to restart the db instance if you're just getting to this now:

```
docker compose stop db && docker compose up -d db
```

You'll also need to set the following env to tell Jupyter where to find the Django app:

```
WEB_EXTERNAL_HOSTNAME="localhost:8000"
WEB_INTERNAL_HOSTNAME="web:8000"
```

#### OAuth

Jupyter uses the Portal's auth system to decide who can log in. Because of this, there's a bit of local setup involved.

**Note: Because Jupyter uses system auth, make sure your Portal user is not named `root`**

The following shows how to do this manually. To do this automatically in the local environment, you can run the following, then skip to restarting Jupyter below:

```
docker-compose run web python /code/crt_portal/manage.py create_local_oauth --write-to-env
```

First, you'll need to set OAUTH_PROVIDER_CLIENT_ID and OAUTH_PROVIDER_CLIENT_SECRET. This is basically the username and password for Jupyter to "log in" to the portal. To get these:
1. Go to http://localhost:8000/oauth2_provider/applications
2. Add your app as an application on this page, and add to ID and Secret to the OAUTH_PROVIDER_CLIENT_ID and OAUTH_PROVIDER_CLIENT_SECRET above in .env
    1. Name: "JupyterHub" is fine.
    2. Redirect uris: http://localhost:8001/hub/oauth_callback
    3. Client type: Confidential
    4. Grant type: Authorization Code
    5. Algorithm: HMAC with SHA-2 256 (aka S256)

**NOTE: Make sure to copy the secret key _before_ saving the entry. Once saved, the secret will be hashed and can't be viewed again**

Here's an example of what this will look like:

![example of config from above](https://user-images.githubusercontent.com/15126660/222504478-778ca5ed-417f-4cb5-8eb1-9532e7ecc719.png)

Because Jupyterhub is trusted (as in, controlled by us) you can also set "Skip authorization" on this application in the admin panel (at http://localhost:8000/admin/oauth2_provider/application/1/change) to save users an extra click when they log in for the first time.

You'll need to restart Jupyter for these to take effect:

```
docker compose stop jupyter && docker compose up -d jupyter
```

To understand where and why to put these pieces where we are, let's talk about how OAuth works in general.

The main thing to understand is the initial login process. There's a couple of steps:
1. Checking that the user is okay with our app (/authorize).
2. Checking that the provider is okay with our app (/token).

Tokens expire often but authorization does not. So long as the user still has the app authorized, the app can continue to ask for more tokens on behalf of the user.

Here's the general oauth process (authorzation_code with PKCE). If anything fails or is invalid, an error is ferried back to the user:

```mermaid
sequenceDiagram
participant U as User
participant JF as Client (Frontend)
participant JB as Client (Backend)
participant PF as Provider (Frontend)
participant PB as Provider (Django Backend)

title OAuth: First-time Login

U ->> JF: Tries to go to a page
JF ->> JB: Has user logged in before?
Note left of JB: (No, first time user)
JB ->> PB: Redirect to Provider Oauth [/authorize]
Note left of PB: Verify CLIENT_ID, Start PKCE
PB ->> PF: Show Login screen
PF ->> PB: Verify user credentials
PB ->> JB: If Valid, Send code
JB ->> PB: Send code + PKCE verifier for Token
PB ->> JB: If verified, send token
Note left of PB: Store Token + Expiration
JB ->> JF: Send token to frontend
Note Left of JF: Cache Token
JF ->> U: Redirect to Intended Page
U ->> JF: Requests now include Token
```

### Installing and Running

Running `docker-compose up --build` should install and run the Jupyter server locally.

After it builds (which will take a while the first go around) visit http://localhost:8001/ to access it. Locally, the username is `dev`, and the password is whatever you entered for JUPYTER_DEV_PASSWORD in `.env`.

Upon logging in, you should be taken to a directory of examples. The examples are saved in the codebase, and demonstrate how to query the pre-configured postgres connection, etc.

Note that code _not_ in `examples/` is not saved to any persistent space, and might be lost if/when the Docker instance restarts.

### Dashboard Exports

Jupyter notebooks can be exported piecemeal to the web application.

To set up a notebook for this process:
- Set "export_embed: true" on the notebook metadata
- Hide any unnecessary cells and code using the "hide_input" and "hide" tags for cell metadata.

Then, to convert and port the file over, run:

```
docker-compose run jupyter python3 export_embed.py
```


## Running common tasks

### Migrations

In Django, when you update the data models you need to create migrations and then apply those migrations, you can do that with:

    docker-compose run web python /code/crt_portal/manage.py makemigrations
    docker-compose run web python /code/crt_portal/manage.py migrate

Keep in mind that if you've added new fields to form models (like the report) you'll need to address them on the form edit pages (see ReportEditForm) to prevent new fields being cleared out when edits happen.

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

### Public and private webpages

In production, we use [django-auth-adfs](https://django-auth-adfs.readthedocs.io/) and new endpoints are behind authentication by default. To create a public page, you must update `LOGIN_EXEMPT_URLS` In [settings.py](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/crt_portal/settings.py) to include the endpoint(s) which are to be available without requiring authentication.

We also explicitly add login required to views and functions that need authentication. If you are making a new path that requires authentication, add a test the [login required test class](https://github.com/usdoj-crt/crt-portal/blob/e9856a2b4726df5ad97ecbf84db99b7767f1662c/crt_portal/cts_forms/tests/tests.py#L985).

We also use public and private as a way to separate views into manageable files. In `cts_forms`, private views are in `views.py` and public views are in `views_public.py`.

### Using Feature Flags

Feature flags allow us to turn on and off certain features from the admin console.

These features can be found at `/admin/features`.

Adding, enabling, and disabling features is done through the admin interface, but gating features in code varies depending on the language.

#### Feature Flags in Django Templates

Django templates should all have an ENABLED_FEATURES dictionary available. The values in the dictionary are either True, False, or None if the feature is enabled, disabled, or missing respectively.

For example:

```jinja
Secret feature enabled?: {{ ENABLED_FEATURES.secret_feature }}

{% if ENABLED_FEATURES.secret_feature %}
    The secret feature lives here!
{% endif %}
```

#### Feature Flags in Python

To use a feature flag in python, you can use features.models.Feature.is_feature_enabled. Note that you can use `django.apps` to make importing Feature easier. For example:

```python
from django.apps import apps

Feature = apps.get_model('features', 'Feature')
if Feature.is_feature_enabled('secret-feature'):
    do_secret_thing()
```

#### Feature Flags in Javascript

Our base templates have a global variables with feature status available. To use it:

```javascript
if (ENABLED_FEATURES.secretFeature) {
    do_secret_thing()
}
```

#### Feature Flags in SCSS

Finally, the "html" tag of all base templates has feature classes appended to it, which allows for SCSS rules that will only apply if that feature is enabled:

```scss
.secret-feature span.secret-span {
    color: rainbow;
    display: magical;
}
```

### I18N

Important commands to use during internationalization (i18n):

When you run `makemessages`, Django will search through .py, .txt, and .html files to find strings marked for translation. Django finds these strings through the `gettext` function or its lazy-loading equivalent (in Python) or the `trans` function (in HTML). This adds the marked strings to `.po` files where translators will do their work.

    docker-compose run -w /code/crt_portal/cts_forms web django-admin makemessages --all

If you only want to generate a `.po` file for a single language, specify the language code like so:

    docker-compose run -w /code/crt_portal/cts_forms web django-admin makemessages -l es

If you edit the `.po` file by hand, re-running the `makemessages` command will correct your formatting for you. It's a good idea to run it one final time before committing changes to locale files so that future change commits to these files are clean.

After the strings are translated, the translation can be compiled back to Django-readable `.mo` files using run `compilemessages`:

    docker-compose run -w /code/crt_portal/cts_forms web django-admin compilemessages

Note: Sometimes links should be included in a translation because they might appear in different parts of the sentence in different languages.  If so, you need to change the quotes within the hyperlinks from double quotes to single quote.  eg

```
{% trans "To report civil rights violations, go to <a class='link--blue' href='https://civilrights.justice.gov/report/'>civilrights.justice.gov/report</a>" %} .
```

#### Adding support for a new language

To add support for a new language, first generate a `.po` file for the new language using the `makemessages` command described above. Once the file is generated, open it and set the `Language` metadata item near the top of the file. This value should be either the language name (Spanish, Chinese Traditional, Korean, etc.) or the [language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (es, zh, ko, etc.). In order to [properly translate plurals](https://www.gnu.org/software/gettext/manual/html_node/Translating-plural-forms.html), you will also need to set the `Plural-Forms` metadata item. Translators should provide and/or verify the appropriate value for this field.

Next, use [po-to-xls](https://pypi.org/project/poxls/) to convert the `.po` file to an Excel spreadsheet. This spreadsheet can be generated in a `tmp` or working directory, and should not be commited to source control. This spreadsheet can be distributed to the translation staff to fill in.

    po-to-xls path/to/new/django.po -o /tmp/new-language-translations.xlsx

Once the translation process is complete and the spreadsheet contains the translations, it is time to convert it back into a `.po` file. This `.po` file is transient and should be generated in a `tmp` or working directory. This can be done using the same tool as above:

    xls-to-po <language> /tmp/new-language-translations.xlsx /tmp/updated.po

\* *The `language` argument in the `xls-to-po` command should match the value that was entered in the `Language` metadata field in the original `.po` file.*

At this point, we have `updated.po`, which contains the translated strings, and we have `django.po` which contains some useful comments (e.g. source files and line numbers for each string) that we'd like to preserve. So, the last step is to merge these two files using [msgmerge](https://www.gnu.org/software/gettext/manual/html_node/msgmerge-Invocation.html):

    msgmerge /tmp/updated.po path/to/django.po -o path/to/django.po

`django.po` now contains the comments generated by `makemessages`, along with the translation strings from `updated.po`.

Now that the translations are available, we need to update the `LANGUAGES` variable in `settings.py` to include our new language. Lastly, run `compilemessages` as described above, or rebuild the application with:

    docker-compose up --build

### Hard reset with a fresh database

If your local database is in a wonky state, you might want to try tearing it all down and rebuilding from scratch.

First, shut down any containers you have running locally. Then run:

    docker system prune --volumes

The volumes are the data elements in Docker. Note that you will need to re-create any local user roles after running this command, and the database will be in an empty state, with no complaint records.

:warning: Note that this command will prune **all** containers, images, and caches on your local machine -- not just the crt-portal project.

## Tests

Tests run automatically with repos that are integrated with Circle CI. You can run those tests locally with the following instructions.

To avoid pushing broken code, you can also configure tests to run locally automatically by following the instructions in [.githooks/README.md](.githooks/README.md).

### Unit tests

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
7. If you're lucky your tests will all pass otherwise, inspect the output to find the failing tests and errors to work on!


Run unit test on **MAC**:

You can also run project tests using docker with:

    docker-compose run web python /code/crt_portal/manage.py test cts_forms --parallel

This will run all of the tests located in the [tests](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/tests) folder. where the business logic tests live.

The test suite includes [test_all_section_assignments.py](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/test_all_section_assignments.py), a script that generates a csv in the `/data` folder which has the relevant permutations of form fields and runs the out put from the [section assignment function](https://github.com/usdoj-crt/crt-portal/blob/develop/crt_portal/cts_forms/models.py#L125). If you are updating section assignments, you will want to edit the csv in data/section_assignment_expected.csv to what the new assignment should be. Additionally, if there are new factors to consider for routing, you will want to add those factors to the test so that they are accounted for.

You can also run a subset of tests by specifying a path to a specific test class or module. For example:

    docker-compose run web python /code/crt_portal/manage.py test cts_forms.tests.test_forms.ComplaintActionTests --parallel

We use the unit tests for calculating code coverage. Tests will fail if code coverage is below 89%. You can run code coverage locally with:

    docker-compose run web coverage run --source='.' /code/crt_portal/manage.py test cts_forms --parallel
    docker-compose run web coverage report --fail-under=89 -m

The -m will give you the line numbers in code that that are not tested by any unit tests. You can use that information to add test coverage.

Please keep in mind that the quality of tests is more important than the quantity. Be on the look out for key functionality and logic that can be documented and confirmed with good tests.

🏃‍♀️🏃‍♂️ To speed up your tests, after you have migrated your database at least once, you can run:

    docker-compose run web python /code/crt_portal/manage.py test --settings=crt_portal.test_settings cts_forms

That will create a file locally that tells your machine to not load zip codes on migration. These are not needed for tests and take a while.

Another way to have a speedier experience locally is to not run local stack and ClamAV unless you are testing attachment uploads or email.

### Accessibility test
For accessibility testing with Pa11y, we generally want a test on each unique view. You can run Pa11y locally, _if you have npm installed locally_:

1) If you are doing this for the first time, log into your local admin and make an account for testing at localhost:8000/admin/auth/user/add/ The user name is `pa11y_tester` password is `imposing40Karl5monomial`. **Never** make this account in the dev or staging environments. Circle testing happens in a disposable database and these are not run against live sites. (Prod doesn't use password accounts but no reason to make it there either.)
2) Run `export PA11Y_PASSWORD=imposing40Karl5monomial` in the command line.
3) run
```npm run test:a11y```

This will run all the tests, look in package.json for a listing of tests, if you want to run them individually.
See full accessibility testing guidelines in our [A11y plan](https://github.com/usdoj-crt/crt-portal/blob/develop/docs/a11y_plan.md).

### Code style tests
You can check for Python style issues by running flake8:

    docker-compose run web flake8

If you have a a reason why a line of code shouldn't apply flake8 you can add `# noqa`, but try to use that sparingly.

You can check for JS style issues by running Prettier:

    npm run lint:check

Prettier can automatically fix JS style issues for you:

    npm run lint:write

### Static security test
You can scan the code for potential python security flaws using [bandit](https://github.com/PyCQA/bandit). Run bandit manually:

    docker-compose run web bandit -r crt_portal/

If there is a false positive you can add `# nosec` at the end of the line that is triggering the error. Please also add a comment that explains why that line is a false positive.

### Security scans
We use OWASP ZAP for security scans. Here is an [intro to OWASP ZAP](https://resources.infosecinstitute.com/introduction-owasp-zap-web-application-security-assessments/#gref) that explains the tool. You can also look at the [scan configuration documentation](https://github.com/zaproxy/zaproxy/wiki/ZAP-Baseline-Scan).

You can run and pull down the container to use locally:

    docker pull owasp/zap2docker-weekly

Run OWASP ZAP security scans with docker using the GUI:

    docker run -u zap -p 8080:8080 -p 8090:8090 -i owasp/zap2docker-weekly zap-webswing.sh

you can see the GUI at http://localhost:8080/zap/

Do use caution when using any "attack" tests, we generally run those in local or sandboxed environments.

To stop the container, find the container id with:

    docker container ls

Then you can stop the container with:

     docker stop <container_id>

Run OWASP ZAP security scans with docker using the command line. Here is an example of running the baseline, passive scan locally targeting the development site:

    docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-weekly zap-baseline.py \
    -t https://crt-portal-django-dev.app.cloud.gov/report/ -c .circleci/zap.conf -z "-config rules.cookie.ignorelist=django_language"

That will produce a report locally that you can view in your browser. It will give you a list of things that you should check. Sometimes there are things at the low or informational level that are false positives or are not worth the trade-offs to implement. The report will take a minute or two to generate.

### End-to-End tests

We're using [Playwright](https://github.com/microsoft/playwright-python) for automated end-to-end testing.

To run Playwright tests locally, first install it by running

    pipenv install playwright

Then, run with the following command.

    pipenv run pytest crt_portal/cts_forms/tests/integration/*.py --base-url=http://localhost:8000

These tests are automatically executed for every pull request against a development instance in CircleCI.

They're also executed against development and staging as those releases happen.

Note that any tests which which require authentication are only executed against branches as part of build_and_test, not dev / staging / prod.

## Browser targeting

For the general public facing pages, we regularly test against Microsoft Edge, Internet Explorer 11, and Google Chrome, and occasionally test against Safari and Firefox.

For the staff-only pages, we only support the Microsoft Edge and Google Chrome browsers. Internet Explorer 11 will _not_ work.

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
    cf create-service s3 basic sso-creds

Or, for prod use the following production settings:

    cf create-service aws-rds medium-psql-redundant crt-db
    cf create-service s3 basic-public crt-s3
    cf create-service s3 basic sso-creds

The medium-psql-redundant instance will provide a more resilient database approved for production and sso-creds is a private bucket used for authentication- see more details on that in the [single sign on docs](https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#single-sign-on).

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

A [network policy](https://docs.cloudfoundry.org/devguide/deploy-apps/cf-networking.html#add-policy) needs to be configured to allow communication between our web application and the ClamAV REST API.

Direct traffic from the portal to the ClamAV REST API:

    cf add-network-policy crt-portal-django --destination-app clamav-rest --protocol tcp --port 9000

    cf add-network-policy crt-portal-django --destination-app clamav-rest --protocol tcp --port 9443

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

We leverage the [CircleCI dependency caching](https://circleci.com/docs/2.0/caching/) feature to accelerate the build process. There are times, such as when upgrading to a new runtime version, when it becomes neccesary to clear the cached dependencies manually. This can be done by incrementing the value of the `CACHE_VERSION` environment variable from the CircleCI project settings.

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
    * Finally, push the release branch `git push origin release/<date-of-planned-release>`
    * Create a PR from github repository for the newly pushed branch
    * Ensure base is master while creating the PR

* The app will re-deploy to **stage** if a new PR is merged into a `release/` branch. We do not do this often, but sometimes we want to get fixes in staging before the next release. You should do this in GitHub.
    * Make sure we understand why the PR is updating **stage** instead of going through the normal process -- there should be a good reason as to why.
    * Verify that the PR has a `release/<date-of-planned-release>` branch as a base branch
    * If all looks good, merge the PR via Github "merge" button
    * Verify that tests pass and that the deploy to **stage** succeeded on [CircleCI](https://circleci.com/gh/usdoj-crt).
    * Note: the developer will be responsible for cherry picking or otherwise merging these staging changes back to **dev**.

* The app will deploy to **prod** when the tests pass and a PR is merged into `master`. You can also do this in GitHub once you confirm approval with the product owner. If there are any merge conflicts, you will want to resolve them on the staging branch first.
    * If have not been any PRs directly to the release branch you can merge in GitHub
    * If there are PRs to the release branch merge with gitflow:
     * Approve the relese on GitHub
     * Check out the release branch and do a `git pull origin release/<name-of-release>`
     * Check out the master branch and do a `git pull origin master`
     * Check out the develop branch and do a `git pull origin develop`
     * Run `git flow release finish`
     * Check out the develop branch and do a `git push origin develop`
     * Once that succeeds, check out the master branch do a `git push origin master`

When CircleCI tries to deploy two PRs back-to-back, one of them can fail. In this case, you can restart the failed deploy process by clicking the "Rerun Workflow" button.

**Hot fixes** will be needed when we find urgent bugs or problems with production. This is where git-flow becomes very useful.
To make the fix:
   * Check out the master branch and do a `git pull origin master`
   * Create a branch for your work with `git flow hotfix start <name-your-hotfix>`
       * This will make a new branch based on the master branch with the naming convention `hotfix/name-of-hotfix`
   * Commit and push your branch, make a PR that targets the master branch for review

To deploy the fix:
   * Make sure the product owner is in the loop with any errors and fixes.
   * The reviewer can test the change locally to do the review. once the reviewer is happy with it:
   * Make sure your branches are up to date
       * Check out the development branch and do a `git pull origin develop`
       * Check out the master branch and do a `git pull origin master`
   * Finish the hotfix with `git flow hotfix finish` This command will make sure that the fix is merged into the master and develop branches. Making sure the change is in both places, means you can test it on dev and your change won't get clobbered later.
   * Push to the develop branch, that now has the fix to trigger a deploy to the dev enviornment
   * Check that the update deployed correctly.
   * Once sastisfied, go to GitHub to approve and merge the PR
   * That will trigger a new build with the fix. Check that the fix worked

The [git-flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/) is a great explainer of the git-flow tool.

## Additional documentation

For more technical documentation see the [docs](https://github.com/usdoj-crt/crt-portal/tree/develop/docs)

- [A11y testing plan](./docs/a11y_plan.md)
- [Branching strategy](./docs/Branching_strategy.md)
- [Maintenance or infrequent tasks](./docs/maintenance_or_infrequent_tasks.md)
- [Pull request instructions](./docs/pull_requests.md)
- [Monitoring](./docs/monitoring.md)

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
