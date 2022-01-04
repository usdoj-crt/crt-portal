"""Form widgets"""
from django.forms.widgets import ChoiceWidget, SelectMultiple, DateInput


class UsaRadioSelect(ChoiceWidget):
    input_type = 'radio'
    template_name = 'django/forms/widgets/radio.html'
    option_template_name = '../templates/forms/widgets/usa_radio_option.html'


class CrtPrimaryIssueRadioGroup(ChoiceWidget):
    input_type = 'radio'
    template_name = '../templates/forms/widgets/multiple_inputs.html'
    option_template_name = '../templates/forms/widgets/crt_radio_area_option.html'


class ComplaintSelect(ChoiceWidget):
    input_type = 'select'
    template_name = '../templates/forms/widgets/complaint_select.html'
    option_template_name = '../templates/forms/widgets/multi_select_option.html'

    def __init__(self, *args, **kwargs):
        label = kwargs.pop('label', None)

        ChoiceWidget.__init__(self, *args, **kwargs)

        self.label = label

    def label_for_widget(self):
        return self.label

    def render(self, name, value, attrs=None, renderer=None):
        extra_context = {
            'label': self.label_for_widget()
        }
        context = self.get_context(name, value, attrs)
        context.update(extra_context)

        return self._render(self.template_name, context, renderer)


class CrtMultiSelect(SelectMultiple):
    template_name = '../templates/forms/widgets/multi_select.html'
    option_template_name = '../templates/forms/widgets/multi_select_option.html'


class CrtDateInput(DateInput):
    input_type = 'date'

# Overrides Django CheckboxSelectMultiple:
# https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#checkboxselectmultiple


class UsaCheckboxSelectMultiple(ChoiceWidget):
    allow_multiple_selected = True
    input_type = 'checkbox'
    template_name = 'django/forms/widgets/checkbox_select.html'
    option_template_name = '../templates/forms/widgets/usa_checkbox_option.html'

    def use_required_attribute(self, initial):
        # Don't use the 'required' attribute because browser validation would
        # require all checkboxes to be checked instead of at least one.
        return False

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False

    def id_for_label(self, id_, index=None):
        """"
        Don't include for="field_0" in <label> because clicking such a label
        would toggle the first checkbox.
        """
        if index is None:
            return ''
        return super().id_for_label(id_, index)


class DataAttributesSelect(ChoiceWidget):
    input_type = 'select'
    template_name = 'django/forms/widgets/select.html'
    option_template_name = 'django/forms/widgets/select_option.html'

    def __init__(self, attrs=None, choices=(), data={}):
        super().__init__(attrs, choices)
        self.data = data

    def create_option(self, name, value, label, selected, index, **kwargs):
        option = super().create_option(name, value, label, selected, index, **kwargs)
        # Prior to Django 3.1, self.data.get(value, {}) worked properly.
        # Beginning in Django 3.2, this results in a `TypeError: unhashable type:
        # 'ModelChoiceIteratorValue` error message. This may be fixed in Django v4
        # when ModelChoiceIteratorValue is made hashable.
        # See patch here: https://code.djangoproject.com/ticket/33155
        # Currently, the fix is to force the `value` to be its original (and
        # hashable) numeric value. Note that there is a blank value that must
        # be skipped.
        if not value.__str__() == '':
            data_attributes = self.data.get(int(value.__str__()), {})
            for key, value in data_attributes.items():
                option['attrs'][f"data-{key}"] = value

        return option


class CRTDateField(DateInput):
    input_type = 'text',
    template_name = '../templates/forms/widgets/crt_date_entry.html'
