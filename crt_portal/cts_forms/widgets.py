from django.forms.widgets import ChoiceWidget


class UsaRadioSelect(ChoiceWidget):
    input_type = 'radio'
    template_name = 'django/forms/widgets/radio.html'
    option_template_name = '../templates/forms/widgets/usa_radio_option.html'
