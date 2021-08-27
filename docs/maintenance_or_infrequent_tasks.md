# Maintenance or infrequent tasks
[:arrow_left: Back to Documentation](../docs)

## Change protected class options

The PROTECTED_CLASS_FIELDS control the order that they fields show up, the nickname of the filed for the CRT view and the variable sometimes used by the model. We derrive three variables from PROTECTED_CLASS_FIELDS: PROTECTED_CLASS_CHOICES determine what is populated in the form. PROTECTED_MODEL_CHOICES determine what is allowable data in the models. PROTECTED_CLASS_CODES are what we display in the crt backend.

So for the old record, we don't want to change them, because we don't know how people replied to the form, but going forward, we don't want to give "National origin (including ancestry, ethnicity, and language)" as an option on the form anymore.

To do that, we would keep that and add the new classes "National origin" and "Identity" in PROTECTED_CLASS_FIELDS. We don't change any of the old data. Make sure you have the correct order to the new elements. You may need to write a targeted data script if you need to converge or merge records. An example would be crt_portal/cts_forms/migrations/0049_fix_other_duplicates.py

If you want to keep the old record as is, write a migration to remove the sort order from the old object and make sure it is not listed in PROTECTED_CLASS_FIELDS. Also adjust the other filed's sort order as needed.

We would then make sure that the "Other" javascript was pointed at the correct element.The "Other" options needs to be last because the other reason explanation text question is implemented as a separate question below the protected class question.

To rename existing models, change the name in model_variables.py PROTECTED_CLASS_FIELDS and create a data migration like: crt_portal/cts_forms/migrations/0045_alter_protected_class_choices.py.

You should be able to reorder the form by setting the value in the database or making a data migration to update the protected classes and form_order. Do NOT use the Django admin for this task, you can [use the Django shell](#use-the-django-shell) to help figure out what the migration should be.

## Add a new optional form
See example code here: https://github.com/usdoj-crt/crt-portal/pull/209/files

1) Make any model changes in models.py, such as new fields. Create and then apply the migration

2) Make a form class in forms.py. You can inherit pieces of other forms if this form is similar to another.

3) make a function to determine when you want the form to show on the front end

4) Add the form class and the function to urls.py

5) In views.py
    - add the new page name for the form page `to all_step_names`
    - add the top-line title for the page to `ordered_step_titles`
    - add an existing or template to the `TEMPLATES` list

## Debugging tips

### Front end
If you are trying to figure out what variables are getting passed to the template you can add the following code in any template:

    <pre> {% filter force_escape %} {% debug %} {% endfilter %} </pre>

### Back end
#### Use the Django shell
SSH into a docker image so you have local database access, (your image may have a different name)

    docker exec -it crt-portal_web_1 /bin/bash

get into the project directory where we can run the Django shell

    cd crt_portal
    python manage.py shell

This takes you into an interactive shell it adds `>>>` to the beginning of lines

import your models or whatever you are working with

    from cts_forms.models import *

Start typing and try out code interactively.

#### pdb
The built in python debugger is good for setting traces.
See the [pdb documentation](https://docs.python.org/3.8/library/pdb.html) for details

## Single sign on
#### Setting environment variables
Request the set up with JMD. When they get things set up on their side, they will be able to supply:
    AUTH_CLIENT_ID
    AUTH_SERVER
    AUTH_USERNAME_CLAIM
    AUTH_GROUP_CLAIM

Those variables need to be set, as well as the secret key if you already have VCAPSERVICES. You can check the current settings first, in case you need to revert them with:

    cf env crt-portal-django

Update VCAP_SERVICES it with the following command, replacing `<value` with the correct value in double quotes.

    cf uups VCAP_SERVICES -p '{"SECRET_KEY":<value>,"AUTH_CLIENT_ID":<value>,"AUTH_SERVER": <value>,"AUTH_USERNAME_CLAIM":<value>,"AUTH_GROUP_CLAIM":<value>, "NEW_RELIC_LICENSE_KEY":<value>}'

You can check that it is in the environment correctly with:

    cf env crt-portal-django

Note that you need to redeploy or restage for the changes to take effect.

The other variables to set are `AUTH_RELYING_PARTY_ID` and `AUTH_AUDIENCE` these are based on the url are not sensitive so they can be put into the manifest. See the prod and stage manifests for examples.

### Adding the ca bundle to S3

JMD will also be able to provide you with a certificate bundle. We will want that in a private S3 bucket.

If it doesn't already exist in the environment, create a private bucket called `sso-creds`. See [cloud.gov S3 documentation](https://cloud.gov/docs/services/s3/) for more details.

    cf create-service s3 basic sso-creds

Then you can connect to the bucket and upload the file using the AWS command line tools [these commands](https://cloud.gov/docs/services/s3/#using-the-s3-credentials). For that script, `SERVICE_INSTANCE_NAME=sso-creds` and
`KEY_NAME=sso-creds-key`. Some local installs may be required.

Upload the certificates to `sso/ca_bundle.pem` in the private bucket. Using the AWS CLI.

    aws s3 cp ./your-path-to-ca-bundle-file s3://${BUCKET_NAME}/sso/ca_bundle.pem

Add `sso-creds` to the seervices part of the manifest. That will bind the bucket to the app on deploy. To add sso to another environment, follow the steps above and add the AUTH_RELYING_PARTY_ID and AUTH_AUDIENCE to the relevant manifest.

Make sure to update the auth settings to include the new environment.

See documentation for the ADFS Django package- https://django-auth-adfs.readthedocs.io/en/latest/

### Code changes

Add the environment to add auth urls condition in urls.py and adding the environment to the auth conditions of settings.py.

crt_portal/crt_portal/settings.py

    # for AUTH, probably want to add stage in the future
    -if environment == 'PRODUCTION':
    +if environment in ['PRODUCTION', 'STAGE']:
         INSTALLED_APPS.append('django_auth_adfs')


crt_portal/crt_portal/urls.py

    environment = os.environ.get('ENV', 'UNDEFINED')
    -if environment == 'PRODUCTION':
    +if environment in ['PRODUCTION', 'STAGE']:
         auth = [

    ...

    ALLOWED_HOSTS = [
        'civilrights.justice.gov',
        'www.civilrights.justice.gov',
        'crt-portal-django-prod.app.cloud.gov',
        'crt-portal-django-stage.app.cloud.gov',
    ]

# Load testing

We use [locust](https://docs.locust.io/en/stable/what-is-locust.html) for load testing. We don't have this kind of testing automated as part of our release at this time.

The scripts won't work on single sign on, I recommend you upgrade staging to have the same DBs and number of instances and do the test on staging without single sign on. Before you do a test on a live site reach out to cloud.gov at support@cloud.gov to give them a heads up, and check that the test will be held at a good time.

Create an unique username and password in staging so that the script can test internal views. Add those values as variables locally that can be accessed as    `LOAD_TESTER` and `LOAD_PASSWORD`.

If you want to run it locally, and you have set up pipenv you can run it with:

    pipenv shell
    locust -f load_testing/locust.py

Then, you can see the locust interface at [http://localhost:8089/](http://localhost:8089/). From there, you can set the base url, how many users you want to simulate and how quickly those users can log on.

After the test is done, delete the user you made for testing.

# pipenv

    pipenv install

    pipenv shell


# Database upgrades

For staging and prod we use medium-psql-redundant. These instructions are for updating dev to medium-psql-redundant or, could be adapted if you ever needed to move prod to a large-psql-redundant instance. Check the [cloud.gov docs])(https://cloud.gov/docs/services/relational-database/) for any updates or new recommendations.

### Here are instructions of how to upgrade the dev db

1) Install dependencies

Install cf-service connect, it's a cloud.gov tool useful for moving data around
    [https://github.com/cloud-gov/cf-service-connect](https://github.com/cloud-gov/cf-service-connect)
    (Darwin is the Mac binary)
If you don't already have it, install [pgcli](https://postgresapp.com/documentation/cli-tools.html) It is a command line tool for working with postgres

4) Export data

For dev and staging that file can be downloaded locally but for prod it may be better to put the file in the private s3 bucket or somewhere on the DOJ network.

    #In your terminal, signed in to could.gov make sure you are in the correct space:
    cf target -s dev

    # In a separate shell window, connect to the service to setup a direct SSH tunnel and leave it running
    # note the credentials and connection info given in the output
    cf connect-to-service -no-client crt-portal-django crt-db

    # Back in the original window, dump the database outside of the fec-cms directory
    # using the credentials provided in the SSH tab
    pg_dump -f crt_dev_<date>.dump postgres://<username>:<password>@<host>:<port>/<name>

5) Create new database

    cf create-service aws-rds medium-psql-redundant crt-db-new

6) Load data into the new database

    psql postgres://<username>:<password>@<host>:<port>/<name> < crt_dev_<date>.dump

7) check crt-db-new and then rename databases
This will allow us to try the new database and make sure we are happy with it before getting rid of the old database.

check the new data base

    #  Connect to the new db using pgcli
    cf connect-to-service crt-portal-django crt-db-new
    # Do some quick queries to make sure the information loaded correctly
    # list tables
    \dt
    # list some report records
    \ select * from cts_forms_report limit 50;
    # list some user accounts
    select * from auth_user limit 50;
    # exit
    \q

rename databases

    # rename old data base
    cf rename-service crt-db crt-db-old
    # rename new data base
    cf rename-service crt-db-new crt-db

8) Restage or redeploy
Redeploying prevents downtime, so that is what you would want to do for production. You can go to Circle and redeploy the last successful build. The change to what database is being used won't go into effect untill the app is restaged or redeployed.

For dev and staging, you can change the bindigs manually and restage. (It's a bit quicker)

    # unbind old db and bind the new one
    cf unbind-service crt-portal-django crt-db-old
    cf bind-service crt-portal-django crt-db
    # confirm the correct db is bound (look at the name, plan, and bound apps)
    cf services
    # restage
    cf restage crt-portal-django

9) Confirm app is working
Go to the site, log out, log back in, make a distinctive sample record.
```
# Connect to the new db using pgcli
cf connect-to-service crt-portal-django crt-db
# Look for you sample. For this one I made the description 'TESTING_NEW_DB 5/24'
select * from cts_forms_report where violation_summary='TESTING_NEW_DB 5/24'
```
10) Clean up
Delete back up file from your local
Delete crt-db-old from cloud.gov

# Dependency management

Dependencies are installed on each deploy of the application as part of the build process in CircleCI

Our dependencies are defined within the repository, changes to should follow the same branching strategy and development process
as any code changes.

In local development with Docker, you will need to rebuild your containers after updating dependencies with:

```shell
docker-compose build
```

## Python

We use [Pipenv] to manage development and production python dependencies.

With pipenv installed locally, you can update development and production dependencies with the following:

```shell
pipenv update --dev
```

To update dependencies from within the `web` docker container, the approach is slightly different.

```sh
docker-compose run web pipenv update --dev
```

Either approach will result in an updated `Pipfile.lock` files located in your local copy of the codebase, ready for commit and submission of a pull request.

[Pipenv]: https://docs.pipenv.org/


# Periodic tasks

We use Django management commands to execute periodic maintenance, refresh, or other code as necessary.

The [CloudFoundry CLI's run-task](https://docs.cloudfoundry.org/devguide/using-tasks.html) command can be used to submit these for execution manually.

Here's an example of executing the `refresh_trends` management command.

```bash
# Authenticate and target the desired space (dev, staging, or prod)
# Then, submit a task to run the `refresh_trends` management command with:
cf run-task crt-portal-django  -c "python crt_portal/manage.py refresh_trends" --name refresh-trends
```

Your local output of executing the above command will reflect success or failure of the task's submission.

Output, if any, of the command being executed will be be available in the application logs.



# Maintenance Mode

We use an environment variable, `MAINTENANCE_MODE`, to run the application with altered functionality.

To **enable** maintenance mode, we need to set the `MAINTENANCE_MODE` environment variable to `True` and restart all running instances.

> **NOTE**: Cloud Foundry [CLI Version 7](https://docs.cloudfoundry.org/cf-cli/v7.html) is required to use `--strategy rolling`


```shell
cf target -s {target environment}
cf set-env crt-portal-django MAINTENANCE_MODE True
cf restart crt-portal-django --strategy rolling
```

To **disable** maintenance mode and return the application to normal operations, remove the `MAINTENANCE_MODE` variable from the desired environment and restart all running instances.

```shell
cf target -s {target environment}
cf unset-env crt-portal-django MAINTENANCE_MODE
cf restart crt-portal-django --strategy rolling
```

## A list of modified functionality when operating in maintenance mode

URL | Method | Normal | Maintenance mode
----|--------|--------|--------
/report/| GET | Render report form | Render 503 maintenance page

## Email configuration

We use [GovDelivery's Targeted Messaging System (TMS)](https://developer.govdelivery.com/api/tms/) to send outbound email from the application.

### Local development

In local environments, all outbound email is routed to [MailHog](https://github.com/mailhog/MailHog).

Outbound messages sent to MailHog are viewable via the MailHog UI, accessible at http://localhost:8025

[Jim, MailHog's Chaos Monkey,](https://github.com/mailhog/MailHog/blob/master/docs/JIM.md) can be enabled and configured by modifying the `docker-compose.yml` file. This is helpful for testing intermittent connections, rejections, or other failures which may be encountered when attempting to send mail.

For example, this command will enable Jim with a 50% chance to reject an incoming connection.

    mailhog:
        image: mailhog/mailhog
        ports:
          - 1025:1025 # smtp server
          - 8025:8025 # web ui
        command: -invite-jim=1 -jim-accept=0.50

### Development, Staging, and Production

To enable outbound emails, a deployed instance **must** have the following environment variables defined in cloud.gov either via the command line or cloud.gov dashboard.


Variable | Description
---------|-----------
`TMS_AUTH_TOKEN` | TMS API authentication token
`RESTRICT_EMAIL_RECIPIENTS_TO` | `;` delimited string of email addresses which, when non-empty, will prevent outbound email from being sent to any address other than those specified here. We use this to prevent sending unexpected emails from development instances.
`TMS_WEBHOOK_ALLOWED_CIDR_NETS` | `;` delimited string of IP addresses from which we're expecting webhook requests. Requests from all other origins will be rejected. May be set to `*` in development to allow requests from all origins.


Command line example

   ```
   # Authenticate and target desired space
   cf set-env crt-portal-django TMS_AUTH_TOKEN not_a_real_token
   cf set-env crt-portal-django TMS_WEBHOOK_ALLOWED_CIDR_NETS 192.168.0.15/24
   cf set-env crt-portal-django RESTRICT_EMAIL_RECIPIENTS_TO developer.email@example.com;dev@example.com
   # re-stage application
   ```

> **WARNING**:
 If `TMS_AUTH_TOKEN` and `TMS_WEBHOOK_ALLOWED_CIDR_NETS` values are not configured the application will start but `EMAIL_ENABLED` will be set to `False` and the user interface will not provide an option to generate and send emails.
