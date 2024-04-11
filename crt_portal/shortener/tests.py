from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import ShortenedURL


class ShortenedURLAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('SHORTENER_TEST_USER', 'a@a.com', '')
        self.client.force_login(self.superuser)
        if ShortenedURL.objects.first():
            ShortenedURL.objects.delete()

    def test_list(self):
        ShortenedURL.objects.create(destination='https://www.google.com', shortname='google').save()

        target = reverse('admin:shortener_shortenedurl_changelist')
        response = self.client.get(target)
        body = response.content.decode('utf-8')

        self.assertIn('<td class="field-destination">https://www.google.com</td>', body)
        self.assertIn('<a href="/link/google">/link/google</a>', body)

    def test_list_disabled(self):
        ShortenedURL.objects.create(destination='https://www.google.com', shortname='google', enabled=False).save()

        target = reverse('admin:shortener_shortenedurl_changelist')
        response = self.client.get(target)
        body = response.content.decode('utf-8')

        self.assertIn('<td class="field-destination">https://www.google.com</td>', body)
        self.assertIn('This must be enabled and saved for the link to work.', body)

    def test_change(self):
        ShortenedURL.objects.create(destination='https://www.google.com', shortname='google', enabled=False).save()
        form_data = {
            'shortname': 'google-changed',
            'destination': '/form/view',
            'enabled': 'on',
            'current_shortname': 'google',
            '_save': 'Save',
        }
        target = reverse('admin:shortener_shortenedurl_change', args=['google'])

        self.client.post(target, form_data, follow=True)

        urls = ShortenedURL.objects.all()
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0].shortname, 'google-changed')
        self.assertEqual(urls[0].destination, '/form/view')
        self.assertEqual(urls[0].enabled, True)


class UrlifyTest(TestCase):
    def test_urlify_replaces_chars(self):
        self.assertEqual(ShortenedURL.urlify('a B_C-d!@#e'), 'a-b-c-d-e')

    def test_urlify_identifies_duplicates(self):
        ShortenedURL.objects.create(shortname='abc').save()
        self.assertEqual(ShortenedURL.urlify('abc'), 'abc-1')

        ShortenedURL.objects.create(shortname='abc-1').save()
        self.assertEqual(ShortenedURL.urlify('abc'), 'abc-2')

    def test_urlify_with_prefix(self):
        self.assertEqual(ShortenedURL.urlify('abc', prefix='foo/'), 'foo/abc')

    def test_urlify_route(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('SHORTENER_TEST_USER', 'a@a.com', '')
        self.client.force_login(self.superuser)

        response = self.client.get('/link/urlify/?name=Hooray%20for%20me')

        self.assertEqual(response.json()['url'], 'hooray-for-me')
