from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth.views import LogoutView

from .. import views


class TestUrls(SimpleTestCase):
    def test_login_url(self):
        url = reverse('auth:login')
        self.assertEqual(resolve(url).func.view_class, views.LoginView)

    def test_logout_url(self):
        url = reverse('auth:logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_registration_url(self):
        url = reverse('auth:registration')
        self.assertEqual(resolve(url).func.view_class, views.RegistrationView)
