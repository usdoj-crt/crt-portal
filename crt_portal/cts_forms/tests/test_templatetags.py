from django.template import Context, Template
from django.test import SimpleTestCase


class MultiselectSummaryTest(SimpleTestCase):
    TEMPLATE = Template('{% load multiselect_summary %} {{ selected|multiselect_summary:"default text" }} ')

    def test_none_selected(self):
        rendered = self.TEMPLATE.render(Context({"selected": []}))
        self.assertIn("default text", rendered)

    def test_one_selected(self):
        rendered = self.TEMPLATE.render(Context({"selected": ["One"]}))
        self.assertIn("One", rendered)

    def test_two_selected(self):
        rendered = self.TEMPLATE.render(Context({"selected": ["One", "Two"]}))
        self.assertIn("One, Two", rendered)

    def test_three_selected(self):
        rendered = self.TEMPLATE.render(Context({"selected": ["One", "Two", "Three"]}))
        self.assertIn("Multi (3)", rendered)
