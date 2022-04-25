from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class FormLettersIndexTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "cookiemonster@fake.net", "")
        self.client.login(username="USER_1", password="")  # nosec
        self.url = reverse('api:form-letters')

    def tearDown(self):
        self.user.delete()

    def test_unauthenticated_user_cant_access_url(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_format(self):
        url = f'{self.url}?start_date=4-12-2022&end_date=4-13-2022'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


class ResponseTitleListTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("USER_1", "cookiemonster@fake.net", "")
        self.client.login(username="USER_1", password="")  # nosec
        self.url = reverse('api:response-titles')

    def tearDown(self):
        self.user.delete()

    def test_unauthenticated_user_cant_access_url(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_access_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
