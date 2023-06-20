from django.test import TestCase
from django.urls import reverse


class BaseTest(TestCase):
    def setUp(self):
        self.first_name = 'Test'
        self.last_name = 'Test'
        self.password = 'PassE228'
        self.email = 'testemail@gmail.com'

        self.registration_url = 'auth:registration'
        self.registration_template = 'authentication/registration.html'
        self.registration_data = {
            'email': self.email ,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password,

        }

        return super().setUp()


class TestRegistrationView(BaseTest):
    def test_registration_get(self):
        response = self.client.get(reverse(self.registration_url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.registration_template)

    def test_registration_invalid_post(self):
        response = self.client.post(reverse(self.registration_url), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.registration_template)

    def test_registration_valid_post(self):
        response = self.client.post(reverse(self.registration_url), data=self.registration_data)
        self.assertEqual(response.status_code, 302)

