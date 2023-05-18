from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth.views import LogoutView

from .. import views


class TestUrls(SimpleTestCase):
    def test_book_api_url(self):
        url = reverse('main:book_api', kwargs={'slug_info': 'test', 'start_date': 'test'})
        self.assertEqual(resolve(url).func, views.book_view_api)

    def test_index_api_url(self):
        url = reverse('main:index')
        self.assertEqual(resolve(url).func.view_class, views.IndexView)

    def test_location_url(self):
        url = reverse('main:location')
        self.assertEqual(resolve(url).func, views.get_location_name)

    def test_search_result_url(self):
        url = reverse(
            'main:search_result',
            kwargs={
                'start_location': 'test',
                'end_location': 'test',
                'start_date': 'test',
                'passenger_number': 1,
            }
        )
        self.assertEqual(resolve(url).func, views.get_flights)

    def test_book_ticket_url(self):
        url = reverse(
            'main:book_ticket',
            kwargs={
                'slug_info': 'test',
                'start_date': 'test',
                'passenger_number': 1,
            }
        )
        self.assertEqual(resolve(url).func.view_class, views.BookView)

    def test_success_payment_url(self):
        url = reverse('main:success_payment')
        self.assertEqual(resolve(url).func.view_class, views.SuccessPayment)

    def test_cancel_payment_url(self):
        url = reverse('main:cancel_payment')
        self.assertEqual(resolve(url).func.view_class, views.CancelPayment)

    def test_payment_url(self):
        url = reverse(
            'main:payment',
            kwargs={
                'name': 'test',
                'total': 100,
                'amount': 1
            }
        )
        self.assertEqual(resolve(url).func.view_class, views.PaymentView)

    def test_cabinet_url(self):
        url = reverse('main:cabinet')
        self.assertEqual(resolve(url).func.view_class, views.PassengerCabinetView)

    def test_user_flights_url(self):
        url = reverse('main:user_flights', kwargs={'user_flights': 'test'})
        self.assertEqual(resolve(url).func, views.get_user_flights)
