from django.test import TestCase
from unittest import mock
from utils import markdown_extensions
import markdown
import os
import textwrap


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

    _TEST_OPTION_CONTENT = textwrap.dedent(r"""
        Non-optional 1
        [%optional group="Group 1" name="Your First Option"]
        This is the first option.
        It has multiple paragraphs.

        [%endoptional]
        Non-optional 2

        [% optional group="Group 2" name="Group 2 option 1"]
        This is the first option of group 2.
        [% endoptional ]

        [% optional group="Group 1" name="Your Second Option" ]
        This is the second option.
        [% endoptional ]
        Non-optional 3
    """)

    def test_get_optionals(self):
        content = self._TEST_OPTION_CONTENT

        optionals = markdown_extensions.get_optionals(content)

        self.assertEqual(optionals, {
            "Group 1": [
                {
                    "group": "Group 1",
                    "name": "Your First Option",
                    "content": "This is the first option.\nIt has multiple paragraphs.",
                    "start_char": 16,
                    "end_char": 138,
                },
                {
                    "group": "Group 1",
                    "name": "Your Second Option",
                    "content": "This is the second option.",
                    "start_char": 263,
                    "end_char": 362,
                }
            ],
            "Group 2": [
                {
                    "group": "Group 2",
                    "name": "Group 2 option 1",
                    "content": "This is the first option of group 2.",
                    "start_char": 155,
                    "end_char": 261,
                }
            ]
        })

        self.assertEqual(content[155:261], textwrap.dedent(r"""
            [% optional group="Group 2" name="Group 2 option 1"]
            This is the first option of group 2.
            [% endoptional ]
        """).strip())

    def test_process_optionals(self):
        content = self._TEST_OPTION_CONTENT

        extension = markdown_extensions.OptionalExtension(include={
            'Group 1': ['Your Second Option'],
            'Group 2': ['Group 2 option 1'],
        })

        rendered = markdown.markdown(content, extensions=[extension])

        self.assertEqual(rendered, textwrap.dedent(r"""
            <p>Non-optional 1</p>
            <p>Non-optional 2</p>
            <p>This is the first option of group 2.</p>
            <p>This is the second option.</p>
            <p>Non-optional 3</p>
        """).strip())
