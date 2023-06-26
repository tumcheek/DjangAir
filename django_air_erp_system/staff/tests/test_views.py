from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from authentication.models import PassengerModel
from .. import models
from main import models


class BaseTest(TestCase):
    def setUp(self):
        # self.first_name = 'Test'
        # self.last_name = 'Test'
        self.password = 'PassE228'
        self.email = 'test@test.com'
        self.gate_manager = PassengerModel.objects.create_user(
            email=self.email,
            password=self.password,
            is_staff=True
        )
        self.gate_manager_group = Group.objects.create(name='gate_managers')
        self.gate_manager.groups.add(self.gate_manager_group)
        self.gate_manager.save()
        self.supervisor_email = 'test@super.com'
        self.supervisor = PassengerModel.objects.create_user(
            email=self.supervisor_email,
            password=self.password,
            is_staff=True
        )
        self.supervisor_group = Group.objects.create(name='supervisors')
        self.supervisor.groups.add(self.supervisor_group)
        self.supervisor.save()

        self.login_url = 'auth:staff-login'
        self.login_gate_manager_data = {
            'email': self.gate_manager.email,
            'password': self.password
        }
        self.login_supervisor_data = {
            'email': self.gate_manager.email,
            'password': self.password
        }
        self.start_location = 'test'
        self.end_location = 'test'
        self.start_date = '2023-04-29'
        self.time = '11:50'
        self.airplane = models.AirplaneModel.objects.create(
            name='test'
        )
        self.price = models.PriceModel.objects.create(
            price=10
        )

        self.flight = models.FlightModel.objects.create(
            airplane=self.airplane,
            price=self.price,
            start_location=self.start_location,
            end_location=self.end_location,
            start_date=self.start_date,
            end_date=self.start_date,
            start_time=self.time,
            end_time=self.time,
            is_cancelled=False
            )
        self.board_registration_url = 'staff:board-registration'
        self.board_registration_template = 'staff/board_registration.html'
        self.board_registration_data = {
            'ticket_number': 1
        }
        self.gate_manager_url = 'staff:gate-manager'
        self.staff_template = 'staff/index.html'
        self.registration_url = 'staff:staff-registration'
        self.registration_template = 'staff/register_staff.html'
        self.first_name = 'Test'
        self.last_name = 'Test'
        self.registration_email = 'reg@reg.com'
        self.registration_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.registration_email,
            'group': self.gate_manager_group,
            'password': self.password
        }

        self.flights_url = 'staff:flights'
        self.flights_template = 'staff/flights.html'
        self.staff_redirect = 'staff:staff-redirect'
        # self.client.post(reverse(self.login_url), data=self.login_gate_manager_data, format='text/html')
        return super().setUp()


class TestBoardRegistrationView(BaseTest):
    def test_board_registration_get(self):
        self.client.post(reverse(self.login_url), data=self.login_gate_manager_data, format='text/html')
        response = self.client.get(reverse(self.board_registration_url, kwargs={'flight_slug': self.flight.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.board_registration_template)

    def test_board_registration_post(self):
        self.client.post(reverse(self.login_url), data=self.login_gate_manager_data, format='text/html')
        response = self.client.post(
            reverse(self.board_registration_url, kwargs={'flight_slug': self.flight.slug}),
            data=self.board_registration_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.board_registration_template)


class TestGateManagerView(BaseTest):
    def test_gate_manager_get(self):
        self.client.post(reverse(self.login_url), data=self.login_gate_manager_data, format='text/html')
        response = self.client.get(reverse(self.gate_manager_url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.staff_template)


class TestSupervisorView(BaseTest):
    def test_supervisor_get(self):
        self.client.post(reverse(self.login_url), data=self.login_supervisor_data, format='text/html')
        response = self.client.get(reverse(self.gate_manager_url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.staff_template)


class TestStaffRegistrationView(BaseTest):
    def test_registration_get(self):
        self.client.post(reverse(self.login_url), data=self.login_supervisor_data, format='text/html')
        response = self.client.get(reverse(self.registration_url, kwargs={'group': 'supervisors'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.registration_template)

    def test_registration_post(self):
        self.client.post(reverse(self.login_url), data=self.login_supervisor_data, format='text/html')
        response = self.client.post(
            reverse(self.registration_url, kwargs={'group': 'supervisors'}),
            data=self.registration_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.registration_template)


class TestFutureFlights(BaseTest):
    def test_future_flight_test(self):
        self.client.post(reverse(self.login_url), data=self.login_supervisor_data, format='text/html')
        response = self.client.get(reverse(self.flights_url, kwargs={'group': 'supervisors'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.flights_template)


class TestStaffRedirectView(BaseTest):
    def test_staff_redirect_view_get(self):
        self.client.post(reverse(self.login_url), data=self.login_supervisor_data, format='text/html')
        response = self.client.get(reverse(self.staff_redirect))
        self.assertEqual(response.status_code, 302)
