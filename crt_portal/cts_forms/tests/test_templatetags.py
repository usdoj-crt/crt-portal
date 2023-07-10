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


class StaticEmbedTest(SimpleTestCase):
    TEMPLATE = Template(r'{% static_embed "img/phone_70.png" %}')
    EXPECTED = "data:image/png;base64,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"

    def test_renders(self):
        rendered = self.TEMPLATE.render(Context())
        self.assertEquals(rendered, self.EXPECTED)
