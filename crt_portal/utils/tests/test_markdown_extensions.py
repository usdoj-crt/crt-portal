from django.test import TestCase
from unittest import mock
from utils import markdown_extensions
import markdown
import os


class MarkdownExtensionsTests(TestCase):
    def test_html_converts_prod_internal(self):
        content = "Go to [the link](/some/target)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension(for_intake=True)

        with mock.patch.dict(os.environ, {'ENV': 'PRODUCTION'}):
            rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="https://crt-portal-django-prod.app.cloud.gov/some/target">the link</a>', rendered)

    def test_html_converts_prod_external(self):
        content = "Go to [the link](/some/target)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension()

        with mock.patch.dict(os.environ, {'ENV': 'PRODUCTION'}):
            rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="https://civilrights.justice.gov/some/target">the link</a>', rendered)

    def test_html_converts_dev(self):
        content = "Go to [the link](/some/target)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension()

        with mock.patch.dict(os.environ, {'ENV': 'DEVELOP'}):
            rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="https://crt-portal-django-dev.app.cloud.gov/some/target">the link</a>', rendered)

    def test_html_converts_stage(self):
        content = "Go to [the link](/some/target)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension()

        with mock.patch.dict(os.environ, {'ENV': 'STAGE'}):
            rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="https://crt-portal-django-stage.app.cloud.gov/some/target">the link</a>', rendered)

    def test_html_converts_local(self):
        content = "Go to [the link](/some/target)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension()

        with mock.patch.dict(os.environ, {'ENV': 'LOCAL'}):
            rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="http://localhost:8000/some/target">the link</a>', rendered)

    def test_html_ignores_absolute(self):
        content = "Go to [the link](https://justice.gov/crt)"
        extension = markdown_extensions.RelativeToAbsoluteLinkExtension()

        rendered = markdown.markdown(content, extensions=[extension])

        self.assertIn('Go to <a href="https://justice.gov/crt">the link</a>', rendered)
