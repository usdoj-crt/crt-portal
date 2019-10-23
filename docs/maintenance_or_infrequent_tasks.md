# Maintenance or infrequent tasks

## Change protected class options

The PROTECTED_CLASS_CHOICES determine what is populated in the form. PROTECTED_MODEL_CHOICES determine what is allowable data in the models.

For example, let's say there is a new need to track national origin and ethnicity separately. Now we just track "National origin (including ancestry, ethnicity, and language)".

So for the old record, we don't want to change them, because we don't know how people replied to the form, but going forward, we don't want to give "National origin (including ancestry, ethnicity, and language)" as an option on the form anymore.

To do that, we would keep that and add the new classes "National origin" and "Identity" in PROTECTED_MODEL_CHOICES and leave the original option. That way, we don't change any of the old data. To make sure the public facing options are correct, we would remove "National origin (including ancestry, ethnicity, and language)" and add "National origin" and "Identity" in PROTECTED_CLASS_CHOICES. We would then remove the form order from National origin (including ancestry, ethnicity, and language) and add the correct order to the new elements. We would then make sure that the "Other" javascript was pointed at the correct element.

If you change the the ProtectedClass model, you may need to squish the migrations and make a new data load script.

You can reorder the form by setting the value in the database or making a data migration to update the protected classes and form_order.