from django.test import SimpleTestCase

from ..forms import ComplaintActions


class ComplaintActionTests(SimpleTestCase):
    def setUp(self):
        self.form = ComplaintActions()

    def test_get_actions_returns_verb_and_description_for_each_changed_field(self):
        self.form.changed_data = ['field_test']
        self.form.cleaned_data = {'field_test': 'verb'}
        actions = [action for action in self.form.get_actions()]
        self.assertEqual(actions, [("updated field test", " with value verb")])
