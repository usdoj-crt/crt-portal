from django.forms.forms import BoundField

# Adapted from this blog post by Michael Kowalchik (mikepk):
# https://mikepk.com/2010/08/python-django-forms-errors-fieldsets/


class QuestionGroup(object):
    def __init__(self, form, fields, group_name='', help_text='', ally_id='', optional=True, label_cls=None, help_cls=None):
        self.form = form
        self.fields = fields
        self.group_name = group_name
        self.help_text = help_text
        self.optional = optional
        self.ally_id = ally_id
        self.label_cls = label_cls
        self.help_cls = help_cls

    def __iter__(self):
        for name in self.fields:
            field = self.form.fields[name]
            yield BoundField(self.form, field, name)
