# Maintenance or infrequent tasks

## Debugging in Cloud.gov

Sometimes you need to see how things work on the server. As you know, don't test it in production, use environments people are less likely to look at, like dev.

First you can SSH into the app with:

    cf ssh crt-portal-django

Then you will need to activate the environment:

    /tmp/lifecycle/shell

This gets you a terminal where you can test things such as `curl` a url to see if it can access it etc.

For testing things out in the python code, you can use the Django shell.

    cd crt_portal
    python manage.py shell

There you can import the things that you want to test and work on code interactively. See [Django tutorial documentation](https://docs.djangoproject.com/en/2.2/intro/tutorial02/#playing-with-the-api) for an example of the ways you can use the shell.

`Control+D`  to exit the shell then, the SSH session.

## Change protected class options

The PROTECTED_CLASS_CHOICES determine what is populated in the form. PROTECTED_MODEL_CHOICES determine what is allowable data in the models.

For example, let's say there is a new need to track national origin and ethnicity separately. Now we just track "National origin (including ancestry, ethnicity, and language)".

So for the old record, we don't want to change them, because we don't know how people replied to the form, but going forward, we don't want to give "National origin (including ancestry, ethnicity, and language)" as an option on the form anymore.

To do that, we would keep that and add the new classes "National origin" and "Identity" in PROTECTED_MODEL_CHOICES and leave the original option. That way, we don't change any of the old data. To make sure the public facing options are correct, we would remove "National origin (including ancestry, ethnicity, and language)" and add "National origin" and "Identity" in PROTECTED_CLASS_CHOICES. We would then remove the form order from National origin (including ancestry, ethnicity, and language) and add the correct order to the new elements. We would then make sure that the "Other" javascript was pointed at the correct element.

If you change the the ProtectedClass model, you may need to squish the migrations and make a new data load script.

To rename existing models, change the name in model_variables.py and create a data migration like: crt_portal/cts_forms/migrations/0016_rename_more_protected_class.py

You should be able to reorder the form by setting the value in the database or making a data migration to update the protected classes and form_order. (This might not be working, we may need additional work to override the django built in sort order for models.)


# Setting up SSO

- Get the needed metadata in XML from the SSO provider

- Create a private S3 bucket



- Upload metadata to bucket

    SERVICE_INSTANCE_NAME=sso-creds
    KEY_NAME=sso-creds-key
    cf create-service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}"
    S3_CREDENTIALS=`cf service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}" | tail -n +2`
    export AWS_ACCESS_KEY_ID=`echo "${S3_CREDENTIALS}" | jq -r .access_key_id`
    export AWS_SECRET_ACCESS_KEY=`echo "${S3_CREDENTIALS}" | jq -r .secret_access_key`
    export BUCKET_NAME=`echo "${S3_CREDENTIALS}" | jq -r .bucket`
    export AWS_DEFAULT_REGION=`echo "${S3_CREDENTIALS}" | jq -r '.region'`


Set:
METADATA_AUTO_CONF_URL


