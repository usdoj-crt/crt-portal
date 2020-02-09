# Maintenance or infrequent tasks

## Change protected class options

The PROTECTED_CLASS_CHOICES determine what is populated in the form. PROTECTED_MODEL_CHOICES determine what is allowable data in the models.

For example, let's say there is a new need to track national origin and ethnicity separately. Now we just track "National origin (including ancestry, ethnicity, and language)".

So for the old record, we don't want to change them, because we don't know how people replied to the form, but going forward, we don't want to give "National origin (including ancestry, ethnicity, and language)" as an option on the form anymore.

To do that, we would keep that and add the new classes "National origin" and "Identity" in PROTECTED_MODEL_CHOICES and leave the original option. That way, we don't change any of the old data. To make sure the public facing options are correct, we would remove "National origin (including ancestry, ethnicity, and language)" and add "National origin" and "Identity" in PROTECTED_CLASS_CHOICES. We would then remove the form order from National origin (including ancestry, ethnicity, and language) and add the correct order to the new elements. We would then make sure that the "Other" javascript was pointed at the correct element.

If you change the the ProtectedClass model, you may need to squish the migrations and make a new data load script.

To rename existing models, change the name in model_variables.py and create a data migration like: crt_portal/cts_forms/migrations/0016_rename_more_protected_class.py

You should be able to reorder the form by setting the value in the database or making a data migration to update the protected classes and form_order. Do NOT use the Django admin for this task, you can use the Django shell.

The "Other" options needs to be last because the other reason explanation text question is implemented as a separate question below the protected class question.


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

Update VCAPSERVICES it with the following command, replacing `<value` with the correct value in double quotes.

    cf uups VCAP_SERVICES -p '{"SECRET_KEY":<value>,"AUTH_CLIENT_ID":<value>,"AUTH_SERVER": <value>,"AUTH_USERNAME_CLAIM":<value>,"AUTH_GROUP_CLAIM":<value>}'

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

Add the environment to add auth urls condion in urls.py and adding the environment to the auth conditions of settings.py.

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


