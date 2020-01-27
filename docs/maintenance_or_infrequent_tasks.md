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

## Single sign on

Request the set up with JMD. When they get things set up on their side, they will be able to supply:
    AUTH_CLIENT_ID
    AUTH_SERVER
    AUTH_USERNAME_CLAIM
    AUTH_GROUP_CLAIM

Those variables need to be set, as well as the secret key if you already have VCAPSERVICES, you will need to update it with the following command, replacing `<value` with the correct value in double quotes.

    cf uups VCAP_SERVICES -p '{"SECRET_KEY":<value>,"AUTH_CLIENT_ID":<value>,"AUTH_SERVER": <value>,"AUTH_USERNAME_CLAIM":<value>,"AUTH_GROUP_CLAIM":<value>}'

JMD will also be able to provide you with a certificate bundle.

If it doesn't already exist in the environment, create a private bucket called `sso-creds`. See [cloud.gov S3 documentation](https://cloud.gov/docs/services/s3/) on how to do that.

Upload the certificates to `sso/ca_bundle.pem` in the private bucket.

To add sso to another environment, follow the steps above and add the AUTH_RELYING_PARTY_ID and AUTH_AUDIENCE to the relevant manifest.

Make sure to update the auth settings to include the new environment.

