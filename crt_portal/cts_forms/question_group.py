from django.forms.forms import BoundField

class QuestionGroup(object):
    def __init__(self, form, fields, group_name='', help_text='', cls=None):
        self.form = form
        self.fields = fields
        self.group_name = group_name
        self.help_text = help_text
        self.cls = cls

    def __iter__(self):
        for name in self.fields:
            field = self.form.fields[name]
            yield BoundField(self.form, field, name)
