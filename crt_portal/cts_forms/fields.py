from django.forms import ChoiceField

class ChoiceFieldWithExamples(ChoiceField):
    def __init__(self, *, choices=(), choices_to_examples=(), **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
        self.choices_to_examples = choices_to_examples