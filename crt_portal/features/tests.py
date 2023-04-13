import textwrap

from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import TestCase

from .templatetags.feature_context import enabled_features

from .models import Feature


class FeatureTests(TestCase):
    def test_name_validation(self):
        self.assertRaises(ValidationError,
                          lambda: Feature(name='OHNO').full_clean())
        self.assertRaises(ValidationError,
                          lambda: Feature(name='oh no').full_clean())
        self.assertRaises(ValidationError,
                          lambda: Feature(name='123').full_clean())
        self.assertRaises(ValidationError,
                          lambda: Feature(name='oh_no').full_clean())
        Feature(name='oh-yes').full_clean()

    def test_to_camel_case(self):
        feature = Feature(name='test-feature-hooray')

        self.assertEquals(feature.camel_case(), 'testFeatureHooray')

    def test_to_snake_case(self):
        feature = Feature(name='test-feature-hooray')

        self.assertEquals(feature.snake_case(), 'test_feature_hooray')

    def test_to_title_case(self):
        feature = Feature(name='test-feature-hooray')

        self.assertEquals(feature.title_case(), 'Test Feature Hooray')

    def test_is_feature_enabled_true(self):
        feature = Feature(name='test-feature-hooray', enabled=True)
        feature.save()

        self.assertTrue(Feature.is_feature_enabled('test-feature-hooray'))

    def test_is_feature_enabled_false(self):
        feature = Feature(name='test-feature-hooray')
        feature.save()

        self.assertFalse(Feature.is_feature_enabled('test-feature-hooray'))

    def test_is_feature_enabled_not_exists(self):
        self.assertIsNone(Feature.is_feature_enabled('test-feature-hooray'))

    def test_get_html_script_tag(self):
        Feature(name='feature-on', enabled=True).save()
        Feature(name='feature-off').save()
        template = Template(
            '{% load feature_script %}'
            '{% feature_script %}'
        )
        self.assertEquals(
            template.render(Context({})),
            textwrap.dedent("""
                <script>
                    const ENABLED_FEATURES = {"featureOn":true,"featureOff":false};
                    document.documentElement.classList.add(...["feature-on"]);
                </script>
            """)
        )

    def test_is_feature_enabled_template_tag_conditions(self):
        Feature(name='feature-on', enabled=True).save()
        Feature(name='feature-off').save()
        template = Template(
            '{% if ENABLED_FEATURES.feature_on %}good{% endif %}'
            '{% if ENABLED_FEATURES.feature_off %}bad{% endif %}'
            '{% if ENABLED_FEATURES.feature_missing %}bad{% endif %}'
        )
        rendered = template.render(Context(enabled_features({})))

        self.assertEquals(rendered, 'good')

    def test_is_feature_enabled_template_tag(self):
        Feature(name='feature-on', enabled=True).save()
        Feature(name='feature-off').save()
        template = Template(
            'on:{{ ENABLED_FEATURES.feature_on }},'
            'off:{{ ENABLED_FEATURES.feature_off }},'
            'missing:{{ ENABLED_FEATURES.feature_missing }}'
        )
        rendered = template.render(Context(enabled_features({})))

        self.assertEquals(rendered, 'on:True,off:False,missing:')
