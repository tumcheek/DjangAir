from django.test import TestCase
from django.urls import reverse

from .. import models


class BaseTest(TestCase):
    def setUp(self):
        self.first_name = 'Test'
        self.last_name = 'Test'
        self.password = 'PassE228'
        self.passenger = models.PassengerModel.objects.create_user(
            email='test@t.com',
            password=self.password
        )
        self.email = 'test@test.com'
        self.seat_0 = 1
        self.start_location = 'test'
        self.end_location = 'test'
        self.start_date = '2023-04-29'
        self.time = '11:50'
        self.passenger_number = 1
        self.airplane = models.AirplaneModel.objects.create(
            name='test'
        )
        self.price = models.PriceModel.objects.create(
            price=10
        )
        self.seat_type = models.SeatTypeModel.objects.create()
        self.seat = models.SeatModel.objects.create(
            seat_type=self.seat_type,
            airplane=self.airplane,
            seat_number=1
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
        self.flight.seats.add(self.seat)

        self.index_url = 'main:index'
        self.index_template = 'main/index.html'
        self.index_data = {
            'start_location': self.start_location,
            'end_location': self.end_location,
            'start_date': self.start_date,
            'passenger_number': self.passenger_number,
        }

        self.location_url = 'main:location'
        self.location_data = {
            'from': 'test',
            'to': 'test',
            'is_end': True
        }

        self.search_result_url = 'main:search_result'
        self.search_result_template = 'main/search_result.html'

        self.book_ticket_url = 'main:book_ticket'
        self.book_ticket_template = 'main/book_ticket.html'
        self.book_ticket_data = {
            'slug_info': self.flight.slug,
            'start_date': self.start_date,
            'passenger_number': self.passenger_number
        }

        self.book_ticket_post_data = {
            'First name[]': [self.first_name],
            'Last name[]': [self.last_name],
            'email[]': [self.email],
            'seat_0': [self.seat_0]
        }

        self.payment_url = 'main:payment'
        self.payment_data = {
            'name': 'test',
            'total': 100,
            'amount': 1
        }

        self.login_url = 'main:login'
        self.login_data = {
            'username': self.passenger.email,
            'password': self.password
        }

        self.passenger_cabinet_url = 'main:cabinet'
        self.passenger_cabinet_template = 'main/passenger_cabinet.html'

        self.registration_url = 'main:registration'
        self.registration_template = 'main/registration.html'
        self.registration_data = {
            'email': 'testemail@gmail.com',
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': 'PassE228',
            'password2': 'PassE228',

        }

        self.user_flights_url = 'main:user_flights'
        self.user_flights = 'future_flights'

        self.book_view_api_url = 'main:book_api'
        self.book_view_api_data = {
            'slug_info': self.flight.slug,
            'start_date': self.start_date
        }
        return super().setUp()


class TestIndexView(BaseTest):
    def test_index_get(self):
        response = self.client.get(reverse(self.index_url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.index_template)

    def test_index_post_valid_data(self):
        response = self.client.post(reverse(self.index_url), data=self.index_data)
        self.assertEqual(response.status_code, 302)

    def test_index_post_invalid_data(self):
        response = self.client.post(reverse(self.index_url), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.index_template)


class TestGetLocationView(BaseTest):
    def test_get_location_name_with_from_and_to(self):
        response = self.client.get(reverse(self.location_url), data=self.location_data)
        self.assertEqual(response.status_code, 200)

    def test_get_location_name_with_from(self):
        response = self.client.get(reverse(self.location_url), data={'from': 'test'})
        self.assertEqual(response.status_code, 200)


class TestSearchResult(BaseTest):
    def test_search_result_get(self):
        response = self.client.get(reverse(self.search_result_url, kwargs=self.index_data))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.search_result_template)


class TestBookView(BaseTest):
    def test_book_ticket_get(self):
        response = self.client.get(reverse(self.book_ticket_url, kwargs=self.book_ticket_data))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.book_ticket_template)

    def test_book_ticket_post_invalid_data(self):
        response = self.client.post(reverse(self.book_ticket_url, kwargs=self.book_ticket_data))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.book_ticket_template)

    def test_book_ticket_post_valid_data(self):
        response = self.client.post(reverse(self.book_ticket_url, kwargs=self.book_ticket_data),
                                    data=self.book_ticket_post_data)
        self.assertEqual(response.status_code, 302)


class TestBookViewApi(BaseTest):
    def test_book_view_api(self):
        response = self.client.get(reverse(self.book_view_api_url, kwargs=self.book_view_api_data))
        self.assertEqual(response.status_code, 200)
        self.assertIn('flight', response.json())
        self.assertIn('seats', response.json())


class TestPaymentView(BaseTest):
    def test_payment_get(self):
        response = self.client.get(reverse(self.payment_url, kwargs=self.payment_data))
        self.assertEqual(response.status_code, 302)


class TestPassengerCabinet(BaseTest):
    def test_passenger_cabinet_get(self):
        self.client.post(reverse(self.login_url), data=self.login_data, format='text/html')
        response = self.client.get(reverse(self.passenger_cabinet_url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.passenger_cabinet_template)


class TestGetUserFlights(BaseTest):
    def test_get_user_flights(self):
        self.client.post(reverse(self.login_url), data=self.login_data, format='text/html')
        response = self.client.get(reverse(self.user_flights_url, args=[self.user_flights]))
        self.assertEqual(response.status_code, 200)


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
