from django.forms.widgets import ChoiceWidget, SelectMultiple


class UsaRadioSelect(ChoiceWidget):
    input_type = 'radio'
    template_name = 'django/forms/widgets/radio.html'
    option_template_name = '../templates/forms/widgets/usa_radio_option.html'


class CrtRadioArea(ChoiceWidget):
    input_type = 'radio'
    template_name = 'django/forms/widgets/radio.html'
    option_template_name = '../templates/forms/widgets/crt_radio_area_option.html'


class CrtDropdown(ChoiceWidget):
    input_type = 'select'
    template_name = '../templates/forms/widgets/crt_dropdown.html'


class ComplaintSelect(ChoiceWidget):
    input_type = 'select'
    template_name = '../templates/forms/widgets/complaint_select.html'
    option_template_name = '../templates/forms/widgets/multi_select_option.html'


class CrtMultiSelect(SelectMultiple):
    template_name = '../templates/forms/widgets/multi_select.html'
    option_template_name = '../templates/forms/widgets/multi_select_option.html'


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
