from django.forms import BoundField

# Adapted from this blog post by Michael Kowalchik (mikepk):
# https://mikepk.com/2010/08/python-django-forms-errors-fieldsets/


class QuestionGroup(object):
    def __init__(
        self,
        form,
        fields,
        group_name="",
        help_text="",
        ally_id="",
        optional=True,
        label_cls=None,
        help_cls=None,
        extra_validation_fields=None
    ):
        self.form = form
        self.fields = fields
        self.group_name = group_name
        self.help_text = help_text
        self.optional = optional
        self.ally_id = ally_id
        self.label_cls = label_cls
        self.help_cls = help_cls
        self.extra_validation_fields = extra_validation_fields

    def __iter__(self):
        for name in self.fields:
            field = self.form.fields[name]
            yield BoundField(self.form, field, name)

    def errors(self):
        """Return field errors contained within this QuestionGroup"""
        errors = []
        if self.extra_validation_fields:
            fields_to_check = self.fields + self.extra_validation_fields
        else:
            fields_to_check = self.fields

        for f in fields_to_check:
            field_errors = self.form[f].errors
            if field_errors:
                errors += field_errors
        return errors
