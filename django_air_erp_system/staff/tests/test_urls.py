from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class TestUrls(SimpleTestCase):
    def test_redirect_url(self):
        url = reverse('staff:staff-redirect')
        self.assertEqual(resolve(url).func, views.staff_redirect_view)

    def test_gate_manager_url(self):
        url = reverse('staff:gate-manager')
        self.assertEqual(resolve(url).func.view_class, views.GateManagerView)

    def test_supervisor_url(self):
        url = reverse('staff:supervisor')
        self.assertEqual(resolve(url).func.view_class, views.SupervisorView)

    def test_flights_url(self):
        url = reverse('staff:flights', kwargs={'group': 's'})
        self.assertEqual(resolve(url).func, views.get_future_flights)

    def test_staff_registration_url(self):
        url = reverse('staff:staff-registration', kwargs={'group': 's'})
        self.assertEqual(resolve(url).func.view_class, views.StaffRegistrationView)

    def test_cancel_flight_url(self):
        url = reverse('staff:cancel-flight', kwargs={'group': 's', 'flight_slug': 'slug'})
        self.assertEqual(resolve(url).func, views.cancel_flights)

    def test_uncancel_flight_url(self):
        url = reverse('staff:uncancel-flight', kwargs={'group': 's', 'flight_slug': 'slug'})
        self.assertEqual(resolve(url).func, views.uncancel_flights)

    def test_board_registration_url(self):
        url = reverse('staff:board-registration', kwargs={'flight_slug': 'slug'})
        self.assertEqual(resolve(url).func.view_class, views.BoardRegistrationView)
