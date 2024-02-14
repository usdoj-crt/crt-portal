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

1. Make any model changes in models.py, such as new fields. Create and then apply the migration

2. Make a form class in forms.py. You can inherit pieces of other forms if this form is similar to another.

3. make a function to determine when you want the form to show on the front end

4. Add the form class and the function to urls.py

5. In views.py
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

# Adding mock reports

To add mock reports for local testing, run the create_mock_reports command with the number of reports you want.

For example, run

`docker-compose run web python crt_portal/manage.py create_mock_reports 10`

to generate 10 reports.

If you need to modify reports for individual testing needs, you can do it temporarily in the python file. For example, if you wanted to test performance of the SQL command that generates the #Total column on "view/form", uncomment

`# report.contact_email = "test@test.test"`

in "create_mock_reports.py" to create multiple reports with the same email address.

# Load testing

We use [locust](https://docs.locust.io/en/stable/what-is-locust.html) for load testing. We don't have this kind of testing automated as part of our release at this time.

The scripts won't work on single sign on, I recommend you upgrade staging to have the same DBs and number of instances and do the test on staging without single sign on. Before you do a test on a live site reach out to cloud.gov at support@cloud.gov to give them a heads up, and check that the test will be held at a good time.

Create an unique username and password in staging so that the script can test internal views. Add those values as variables locally that can be accessed as `LOAD_TESTER` and `LOAD_PASSWORD`.

If you want to run it locally, and you have set up pipenv you can run it with:

    pipenv shell
    locust -f load_testing/locust.py

Then, you can see the locust interface at [http://localhost:8089/](http://localhost:8089/). From there, you can set the base url, how many users you want to simulate and how quickly those users can log on.

After the test is done, delete the user you made for testing.

# pipenv

    pipenv install

    pipenv shell

# Database upgrades

For staging and prod we use the `medium-psql-redundant` database service. These instructions are for updating dev to `medium-psql-redundant` and can be adapted to move prod to a `large-psql-redundant` instance. Check the [cloud.gov docs](https://cloud.gov/docs/services/relational-database/) for any updates or new recommendations.

### Here are instructions of how to upgrade the dev db

1. **Install dependencies.**

   - Install [`cf-service-connect`](https://github.com/cloud-gov/cf-service-connect), a cloud.gov tool for moving data around
     [https://github.com/cloud-gov/cf-service-connect](https://github.com/cloud-gov/cf-service-connect)
     (Darwin is the Mac binary)
   - If you don't already have it, install [`pgcli`](https://postgresapp.com/documentation/cli-tools.html), a command line tool for working with PostgreSQL.

2. **Sign into cloud.gov and set `cf target` to desired instance.** This gives you command line access to the instance.

   ```sh
   cf login -a api.fr.cloud.gov --sso
   ```

   Enter the passcode from the URL that is given to you, and make sure you select the correct organization and space.

   ```sh
   cf target -s dev
   ```

3. **Export data from existing database.** Database dumps from dev and staging instances can be downloaded locally, but for prod it may be better to put the file in the private s3 bucket or somewhere on the DOJ network.

   In a separate shell window, connect to the service to setup a direct SSH tunnel and leave it running. Note the credentials and connection info given in the output.

   ```sh
   cf connect-to-service -no-client crt-portal-django crt-db
   ```

   Back in the original window, dump the database outside of the project directory using the credentials provided in the SSH tab.

   ```sh
   pg_dump -f crt_dev_<date>.dump postgres://<username>:<password>@<host>:<port>/<name>
   ```

   After the dump has finished, you can return to the SSH tab and press Control-C to close the tunnel.

4. **Create new database.**

   ```sh
   cf create-service aws-rds medium-psql-redundant crt-db-new
   ```

   You can run `cf services` to see that the new database is being created. Wait for it to finish creating before proceeding to the next step.

5. **Load data into the new database.**

   After the new database has been created, open a new shell window and open a SSH tunnel to the new database. Again, note the credentials and connection info in the output.

   ```sh
   cf connect-to-service -no-client crt-portal-django crt-db-new
   ```

   Back in the original window, load the database from the dumped file using the credentials for the new database.

   ```sh
   psql postgres://<username>:<password>@<host>:<port>/<name> < crt_dev_<date>.dump
   ```

   You may see some errors because the new database doesn't have the same roles. This is fine: roles could only be preserved by running `pg_dumpall` command on the original database, and we didn't do that because we do not have access to run that on `shared_psql` instances. The data will still be loaded just fine.

   After the data has been loaded, close the SSH tunnel.

6. **Check the new database.** This is a gut-check to make sure that the data has populated the new database.

   ```sh
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
   ```

7. **Rename databases.** This will allow us to try the new database and make sure we are happy with it before getting rid of the old database.

   ```sh
   # rename old data base
   cf rename-service crt-db crt-db-old

   # rename new data base
   cf rename-service crt-db-new crt-db
   ```

8. **Restage or redeploy.** The change to what database is being used won't go into effect until the app is restaged or redeployed.

   Redeploying prevents downtime, so that is what you would want to do for production. You can go to Circle and redeploy the last successful build.

   For dev and staging, you can change the bindings manually and restage. (It's a bit quicker)

   ```sh
   # unbind old db and bind the new one
   cf unbind-service crt-portal-django crt-db-old
   cf bind-service crt-portal-django crt-db

   # confirm the correct db is bound (look at the name, plan, and bound apps)
   cf services

   # restage
   cf restage crt-portal-django
   ```

9. **Confirm app is working.** Go to the site, log out, log back in, make a distinctive sample record.

   ```sh
   # Connect to the new db using pgcli
   cf connect-to-service crt-portal-django crt-db

   # Look for your sample. For this one I made the description 'TESTING_NEW_DB 5/24'
   select * from cts_forms_report where violation_summary='TESTING_NEW_DB 5/24'
   ```

10. **Clean up.** Once everything looks good:

    - Delete database dump file from your local machine
    - Delete `crt-db-old` from cloud.gov

## Setup Jupyter on Cloud Foundry

Note: All of these `manage.py` commands must be run from an ssh session on a Portal instance (see `Manually running manage.py`).

### 1. Create a Read-only User

Jupyter needs read-only access to the database in order to make queries.

To do this, Django migrations read-only database user on the application database (for a simplified proof of concept and to learn more about how this works, see [this PR](https://github.com/usdoj-crt/crt-portal/pull/1390)).

The migrations happen automatically, but need to be told the username and password to use. To do this, set `POSTGRES_ANALYTICS_USER` and `POSTGRES_ANALYTICS_PASSWORD` (these must be randomly generated, valid postgres credentials):

```shell
cf target -s {target environment}
cf set-env crt-portal-django POSTGRES_ANALYTICS_USER {secret username}
cf set-env crt-portal-django POSTGRES_ANALYTICS_PASSWORD {secret password}
```

Make sure to also update settings.py to set `DATABASES['analytics']` on the instance you're deploying to.

If migrations have already been run, you can either migrate down and up (**which will drop all analytics data**) or add a new migration to create the user.

To migrate down and up, run:

```shell
python manage.py migrate analytics zero
python manage.py migrate analytics
```

To add a new migration, use `analytics.models.make_analytics_user`, for example:

```python
from analytics import models

class Migration(migrations.Migration):
    ...
    operations = models.make_analytics_user()
```

### 2. Configure OAuth

If you haven't deployed Jupyter to Cloud Foundry yet, this one is a bit of a chicken and egg scenario. In order to deploy Jupyter, you must have OAuth configured (or it will throw an exception on startup). However, in order to configure OAuth, Jupyter must be deployed!

The solution is to:

1. Deploy and get the error.
2. Configure OAuth, and redeploy.

So, proceed to step 3, then come back here.

Once the application is deployed, you must create a way for Jupyter to talk to the Portal over internal HTTPS. To do so, run the following **locally**:

```
cf add-network-policy crt-portal-jupyter crt-portal-django
cf add-network-policy crt-portal-django crt-portal-jupyter
```

Note: Make sure that crt-portal-django has an apps.internal route in `manifest_etc.yaml`, and is added to ALLOWED_HOSTS in settings.py

The actual configuration happens in two steps - one of which is run on the portal instance over ssh, and the other of which is run locally:

Over ssh, create the oauth application in our serving postgres. Make sure to swap out `dev` with the correct URI:

```bash
python manage.py create_jupyter_oauth --cf-set-env --redirect_uris="https://crt-portal-jupyter-dev.app.cloud.gov/hub/oauth_callback"
```

Then, copy the output it produces (`cf set-env ...`) and run it locally so that it applies to all of our instances, e.g.:

```bash
cf set-env crt-portal-jupyter OAUTH_PROVIDER_CLIENT_ID some-long-generated-client-id-here && cf set-env crt-portal-jupyter OAUTH_PROVIDER_CLIENT_SECRET some-long-generated-client-secret-here
```

You'll also need to tell it where to find the portal, using the routes from manifest\_\*.yaml - for example, on dev (for regular use, this codified in manifest_etc.yml, not set via cf set-env):

```bash
cf set-env crt-portal-jupyter WEB_EXTERNAL_HOSTNAME "https://crt-portal-django-dev.app.cloud.gov"
cf set-env crt-portal-jupyter WEB_INTERNAL_HOSTNAME "http://crt-portal-django-dev.app.apps.internal:8080"
```

You'll need to restart the serving Jupyter instances for it to read the new environment variables, which can be done by running the following locally:

```bash
cf restart crt-portal-jupyter
```

Once they restart, confirm all is good by logging out of the portal (this can be done from the top right corner of the admin panel), then logging into Jupyter.

### 3. Deploy the Application

So long as there is an entry for crt-portal-jupyter in `manifest_etc.yaml`, the application can be deployed with `cf push` or by merging a pull request. See `manifest_dev.yaml` for an example of how to configure a new cloud foundry space.

Make sure that .circleci/config.yml contains an entry for "Deploy crt-portal-jupyter to (space)" under the relevant section.

### 4. Tell Jupyter the database address

Because Jupyter should _never_ have write access to the database, we can't expose VCAP_SERVICES to it. This means, however, that it also doesn't know the name, address, or port of the database.

To fix that, run the following **locally**. Note that this will restart Jupyter.

This must be run whenever postgres is re-created / re-staged:

```
./sync-jupyter-db.sh
```

## Scheduling Notebooks to Run

Jupyter notebooks can be scheduled to run using the jupyterhub/schedules.json file.

This file expects a list of entries in the following format:

```json
[
  {
    "path": "assignments/intake-dashboard/total_complaints.ipynb",
    "last_executed": "2023-09-15T15:28:00.984824",
    "interval": { "days": 2 }
  }
]
```

Where:

- `path` is the path to the notebook relative to the `jupyterhub/` directory
- `last_executed` can be left blank (this will be updated after each run)
- `interval` will be unpacked to the constructor of datetime.timedelta. Note that the interval is limited by the frequency at which the circleci/config.yml task (`periodic-tasks-jupyter-*` is run.

Note that any files under `assignments/intake-dashboard` are visible from /form/data/dashboard-name. For example, if you have `assignments/intake-dashboard/test.ipynb`, you can go to `/form/data/test` to view it. The page also accepts commas to view multiple dashboards, e.g.: `/form/data/test_1,test_2,test_3`

If a file under `assignments/intake-dashboard` isn't found in `schedules.json`, an entry will be created for it and it will be run hourly until the schedule is updated.

## Response templates

Response templates (for example, form letters) are used by intake specialists to respond to complaints. These are stored as flat text files with YAML front-matter metadata in this location:

```
[BASE_DIR]/crt_portal/cts_forms/response_templates/
```

Files must be named with a `.md` extension. This is intentional. We currently do not use or parse Markdown, but many of our response templates were initially created with light styling in mind (bold, links, even tables). This functionality may be added in the future.

### Template formatting and variables

Files should have the following format:

```yaml
---
title: IER - Form Letter
subject: "Response: Your Civil Rights Division Report - {{ record_locator }} from the {{ section_name }} Section"
language: en
---
{{ addressee }},

You contacted the Department of Justice on {{ date_of_intake }}. After careful review of what you submitted, we have determined that your report would more appropriately be handled by another federal agency.

Your record number is {{ record_locator }}.
```

In the front-matter section, the following properties are required:

- **title**: This is used by staff to identify which letter to send, and it is also a unique identifier for the response template, enforced by our database schema. If a response template matching an existing title is found in the database, it will be updated. If no response template with this title is found, a new entry will be created. (File names are used to identify response templates.)
- **subject**: This is the subject line that will be used when a response is sent via e-mail.
- **language**: This is a two-letter language code for the language that the template is written in. See below for a list of language codes.

Other properties can be added to the front-matter section, but will be ignored. There is one optional property.

- **ignore**: This is a boolean value. If set to `true`, the response template file will not be created or updated in the database. This can be used to prevent a response template from overwriting changes made manually in the database. If this property is missing or set to `false`, the default behavior is to create or update response templates.

The following placeholders are available to use in the text body or in the subject line:

- **`{{ record_locator }}`** - the number-letter ID of a submitted report.
- **`{{ date_of_intake }}`** - the human-readable date that a report was submitted.
- **`{{ section_name }}`** - the name of the section that the report has been assigned to.
- **`{{ addressee }}`** - a boilerplate salutation that includes the reporter's name, if provided.

Placeholders also have locale-specific versions. These can be accessed by prefixing the placeholder with the two-letter language code. For example, this is a response template in Spanish:

```yaml
---
title: IER - Form Letter (Spanish)
subject: "Respuesta: Su informe de la División de Derechos Civiles - {{ record_locator }} de la Sección {{ es.section_name }}"
language: es
---
{{ es.addressee }},

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Tras revisar su presentación detenidamente, hemos determinado que su informe podría ser tratado de una forma más apropiada por otra agencia federal.

Su número de registro es {{ record_locator }}.
```

Note the "es." prefix for variables that are specific to the Spanish language.

The `{{ record_locator }}` variable is the same in every locale and does not need to be prefixed.

#### Language codes

- Spanish = 'es'
- Chinese Traditional = 'zh-hant'
- Chinese Simplified = 'zh-hans'
- Vietnamese = 'vi'
- Korean = 'ko'
- Tagalog = 'tl'
- English = 'en'

### Processing

Response templates are automatically added or updated to the database when the Django server starts.

Response templates are never automatically deleted. If a file is removed from the repository, staff should manually delete the response template in the database if that's desired.

If you want to manually run the command to add or update response templates without restarting the server, run this command:

```sh
docker-compose run web python /code/crt_portal/manage.py update_response_templates
```

### Legacy response templates

Prior to the flat file system, response templates were added or changed in the database with migrations. This was changed to reduce the amount of coordination and error-proneness of using migrations to add and update data.

Templates that have been previously added via a migration may not yet exist as flat files. Over time, we should be able to port those templates into the new format. Please do not add or make changes to response templates with new migrations.

To remove a legacy response template permanently, that should be done with a new migration.

### Adding a department address to a form

Department addresses for referral templates are stored in the database as `cts_forms.models.ReferralContact`

New contacts will need to be added to the admin panel. They can be paired with referral templates using the machine name, for example, if your ReferralContact's `machine_name` is `eeoc`:

```
---
title: CRT - EEOC Referral Form Letter
subject: "Response: Your Civil Rights Division Report - {{ record_locator }} from the {{ section_name }} Section"
language: en
referral_contact: eeoc
---
```

This will cause the referral information to be appended to the top of the printed letter when printing the letter.

Note that this doesn't (yet) affect the content of referral letters, which should still be updated in markdown and checked in to source control.

### Updating forms

Here is example code for modifying an existing form.

```
from django.db import migrations


def update_spanish_PREA(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    spanish_prea_form = ResponseTemplate.objects.get(title='SPL - Referral for PREA Issues (Spanish)')
    # adjust addressee and indentation
    spanish_prea_form.body = """
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Con base en nuestro repaso hasta la fecha, quisiéramos avisarle que tal vez quiera comunicarse con el Coordinador de la PREA [Ley contra la Violación en las Cárceles] de su estado.

Lo que hicimos:

Su número de registro es {{ record_locator }}.

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Con base en su reporte, nuestro equipo determinó que sus preocupaciones están relacionadas con abusos sexuales o acoso sexual estando en la cárcel. Esto podría ser amparado por la ley contra la Violación en las Cárceles (PREA). PREA es una ley que prohíbe:

- abusar sexualmente o acosar sexualmente a reclusos y detenidos o
- tomar represalias contra un recluso o miembro del personal que denuncie el abuso sexual o acoso sexual.

Seguiremos revisando su reporte y nos comunicaremos con usted si necesitamos alguna información adicional. No obstante, cabe destacar que en situaciones que conllevan el abuso sexual o acoso sexual de reclusos y detenidos, la División de Derechos Civiles solo podrá involucrarse cuando existe un patrón generalizado de mala conducta. Por lo tanto, por lo general, no podemos iniciar investigaciones basadas en alegaciones individuales.

En consecuencia, queremos avisarle que el Coordinador de la PREA de su estado podría ayudarle con su situación. Un Coordinador de la PREA puede investigar alegaciones individuales como la suya. Para facilitar su comunicación con el Coordinador de la PREA, hemos incluido un directorio con esta respuesta.

Lo que usted puede hacer:

El Coordinador de la PREA de su estado podría ayudarle con su situación. Para comunicarse con el Coordinador de la PREA de su estado, consulte el directorio adjunto.

Por otra parte, puede aprender más sobre PREA en el sitio web del Centro de Información sobre PREA: www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards (solo en inglés)

Cómo nos ha ayudado:

Su reporte nos ayudará a fomentar los derechos civiles. La información contenida en reportes como el suyo nos ayuda a entender asuntos y tendencias emergentes relacionados con los derechos civiles. Esto, a su vez, nos ayuda a informar cómo protegemos los derechos civiles de todas las personas en este país.

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles

"""
    spanish_prea_form.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0122_auto_reply_form_letter'),
    ]

    operations = [
        migrations.RunPython(update_spanish_PREA)
    ]
```

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
cf run-task crt-portal-django -c "python crt_portal/manage.py refresh_trends" --name refresh-trends -m 512M -k 2G
```

Your local output of executing the above command will reflect success or failure of the task's submission.

Output, if any, of the command being executed will be be available in the application logs.

## Manually running manage.py

Note: Only use this for troubleshooting purposes, if `cf run-task` won't work. The recommended method is to login to cloud.gov ssh console, go to the target space (dev, staging, prod) and cf run-task with appropriate python command.

In the event that period tasks are failing, or that you need to run manage.py from Cloud Foundry (dev, stage, or prod), you can connect to one of the remote instances to troubleshoot and run commands.

Note that this will be one of the actual, user-facing instances - so long-running commands may tie up the instance and cause delays on the site.

A bit of setup is required to get bash to recognize the python dependencies:

```shell
cf target -s your_target_environment
cf ssh crt-portal-django -t -c '\
    export LD_LIBRARY_PATH="$HOME/deps/1/lib:$HOME/deps/0/lib" && \
    export PATH="$PATH:$HOME/deps/1/python/bin/" && \
    cd /home/vcap/app/crt_portal && \
    exec /bin/bash -li \
  '
```

Once you've connected and have a prompt, you can run commands such as:

```shell
python manage.py generate_repeat_writer_info
```

For more about the directory structure of deployed instances, see [cloudfoundry's docs](https://docs.cloudfoundry.org/buildpacks/understand-buildpacks.html#droplet-filesystem).

## Updating the U.S. Web Design System

Our front-end stylesheets and UI components are based on the [U.S. Web Design System (USWDS)](https://designsystem.digital.gov/). We want to track updates to the USWDS closely whenever possible in order to adopt the most recent guidance in user experience, developer experience, and accessibility, and to keep our product up-to-date with other modern federal government websites. Update cadence should be roughly 1-2 months, but if we're behind, it's best to update only one minor version at a time (usually okay to include all patch updates) incorporating changes at each step. _Despite following semantic versioning, USWDS v2 can introduce breaking changes at minor versions_.

In general, follow these steps to update the USWDS:

1. Update `package.json` to set the next version of the `uswds` package and run `npm install`.
2. Read the [changelog](https://github.com/uswds/uswds/releases) and incorporate any necessary updates:
   - Update any markup changes (e.g. component code changes, accessibility updates)
   - Adopt new components, if any. The USWDS sometimes introduces new components that can replace custom or third-party UI components that we use, and offloading our work to the USWDS is a one-time effort that makes it easier to maintain these components in the future.
   - Note any other bug fixes or feature improvements that affect or improve our site.
3. Updates to stylesheet and visual assets.
   - Update our settings in `crt_portal/static/sass` from the [source theme](https://github.com/uswds/uswds/tree/develop/src/stylesheets/theme). (You can do a diff between the new version and last version to see new additions.) Don't override settings we set on purpose, but we should add or set new settings.
   - Check that stylesheets can build with `npx gulp build-css`.
     - A common issue is that a new component uses a color value that we set to `false`, which throws an error when Sass tries to resolve a value. Usually, setting it to the default value will resolve the problem.
   - Check for any changes or additions to static files, e.g. images that should be copied to the [static folder](https://github.com/usdoj-crt/crt-portal/tree/develop/crt_portal/static/img).
4. Updates to JavaScript.
   - Copy the minified JavaScript bundles from `node_modules/uswds/dist/js` (installed in step 1) to the `crt_portal/static/vendor` folder.
5. Updates to the Gulp build process. This may not always occur.
   - Update `package.json` to pin to a version of [`uswds-gulp`](https://github.com/uswds/uswds-gulp) that is expected to work with the version of USWDS installed in step 1. `uswds-gulp` does not use versioning, so we pin to a specific commit SHA. This will include changes to build dependencies and `gulpfile.js`, try to incorporate as many updates as possible.
6. Verify that the build process works and that all functionality works as expected.
7. Ready to review and deploy!

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

# Voting Mode

Like Maintenance mode, we use an environment variable, `VOTING_MODE`, to run the application during voting season. This places Voting choice as the primary reason at the top
of the proForm and regular report section, and will add a banner to a page to give users a better sense of their voting rights.

To **enable** voting mode, we need to set the `VOTING_MODE` environment variable to `True` and restart all running instances.

> **NOTE**: Cloud Foundry [CLI Version 7](https://docs.cloudfoundry.org/cf-cli/v7.html) is required to use `--strategy rolling`

```shell
cf target -s {target environment}
cf set-env crt-portal-django VOTING_MODE True
cf restart crt-portal-django --strategy rolling
```

To **disable** voting mode and return the application to normal operations, remove the `VOTING_MODE` variable from the desired environment and restart all running instances.

```shell
cf target -s {target environment}
cf unset-env crt-portal-django VOTING_MODE
cf restart crt-portal-django --strategy rolling
```

## A list of modified functionality when operating in maintenance mode

| URL      | Method | Normal             | Maintenance mode            |
| -------- | ------ | ------------------ | --------------------------- |
| /report/ | GET    | Render report form | Render 503 maintenance page |

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

| Variable                        | Description                                                                                                                                                                                                                             |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TMS_AUTH_TOKEN`                | TMS API authentication token                                                                                                                                                                                                            |
| `RESTRICT_EMAIL_RECIPIENTS_TO`  | `;` delimited string of email addresses which, when non-empty, will prevent outbound email from being sent to any address other than those specified here. We use this to prevent sending unexpected emails from development instances. |
| `TMS_WEBHOOK_ALLOWED_CIDR_NETS` | `;` delimited string of IP addresses from which we're expecting webhook requests. Requests from all other origins will be rejected. May be set to `*` in development to allow requests from all origins.                                |

Command line example

```
# Authenticate and target desired space
cf set-env crt-portal-django TMS_AUTH_TOKEN not_a_real_token
cf set-env crt-portal-django TMS_WEBHOOK_ALLOWED_CIDR_NETS 192.168.0.15/24
cf set-env crt-portal-django RESTRICT_EMAIL_RECIPIENTS_TO developer.email@example.com;dev@example.com
# re-stage application
```

> **WARNING**:
> If `TMS_AUTH_TOKEN` and `TMS_WEBHOOK_ALLOWED_CIDR_NETS` values are not configured the application will start but `EMAIL_ENABLED` will be set to `False` and the user interface will not provide an option to generate and send emails.
