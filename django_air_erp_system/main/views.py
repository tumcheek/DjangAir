import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView as Login
from django.utils import timezone

from .forms import SearchFlightForm, UserLoginForm, RegistrationForm
from . import models
from .form_validator import is_form_data_valid
from .tasks import send_mail_task


def get_flight_options(flight):
    _options = flight.options.all()
    options = []
    for option in _options:
        option_info = {
            'id': option.pk,
            'name': option.name,
            'description': option.description,
            'price': option.price.price
        }
        options.append(option_info)
    return options


def get_flight_info(flight):
    available_seats = flight.seats.count() - flight.tickets.count()
    flight_info = {
        'start_location': flight.start_location,
        'end_location': flight.end_location,
        'start_date': flight.start_date.strftime('%Y-%m-%d'),
        'end_date': flight.end_date.strftime('%Y-%m-%d'),
        'start_time': flight.start_time,
        'end_time': flight.end_time,
        'slug': flight.slug,
        'available_seats': available_seats,
        'options': get_flight_options(flight),
        'price': flight.price.price,
        'is_cancelled': flight.is_cancelled
    }
    return flight_info


def get_flights_info(flights_query, passengers):
    flights = []
    for _flight in flights_query:
        flight = get_flight_info(_flight)
        if flight['is_cancelled'] or (flight['available_seats'] - passengers) < 0:
            continue
        flights.append(flight)
    return flights


def get_type_of_seats():
    _seats_type = models.SeatTypeModel.objects.all()
    seats_type = [(seat_type.get_seat_type_display(), seat_type.pk) for seat_type in _seats_type]
    return seats_type


def get_unavailable_seats(flight):
    flight_tickets = flight.tickets.all()
    tickets_seat = [ticket.seat.seat_number for ticket in flight_tickets]
    return tickets_seat


def get_all_seats(flight):
    seats_type = get_type_of_seats()
    tickets_seat = get_unavailable_seats(flight)
    seats_dict = {}
    for seat_type, type_pk in seats_type:
        seats = flight.seats.filter(seat_type=type_pk)
        seats_dict[seat_type] = [{'number': seat.seat_number,
                                  'is_available': False if seat.seat_number in tickets_seat else True}
                                 for seat in seats]

    return seats_dict


def check_post_fields(request, required_fields, length):
    for field in required_fields:
        if field not in request.POST:
            raise ValidationError(f'Field {field.replace("[]", "")} is required.')
        _field = request.POST.getlist(field)
        if len(_field) != length:
            raise ValidationError(f'Input {field.replace("[]", "")} for all passengers.')
    return True


def is_user_exist(email):
    user = models.PassengerModel.objects.filter(email=email)
    if user:
        return True
    else:
        return False


def generate_password(length=12):
    """
    Generates a random password of the given length
    """
    allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-='
    return get_random_string(length=length, allowed_chars=allowed_chars)


def get_mail_subject(name, subject):
    try:
        mail_subject = models.EmailSubjectModel.objects.get(name=name)
    except ObjectDoesNotExist:
        mail_subject = subject
    return mail_subject


def get_options_price(options):
    _sum = 0
    if options.count() > 0:
        for option in options:
            _sum += option.price.price
    return _sum


def get_ticket_options(options):
    _options = []

    for option in options:
        option_info = {
            'name': option.name,
            'description': option.description,
            'price': option.price.price
        }
        _options.append(option_info)
    return _options


def get_user_tickets(tickets):
    _tickets = []
    for ticket in tickets:
        options = get_ticket_options(ticket.options.all())
        ticket_info = {
            'from': ticket.flight.start_location,
            'to': ticket.flight.end_location,
            'start_date': ticket.flight.start_date,
            'end_date': ticket.flight.end_date,
            'start_time': ticket.flight.start_time,
            'end_time': ticket.flight.end_time,
            'seat': ticket.seat.seat_number,
            'seat_type': ticket.seat.seat_type.get_seat_type_display(),
            'options': options
        }
        _tickets.append(ticket_info)
    return _tickets


def check_is_user_future_flights(ticket):
    flight_date = ticket['start_date'].date()
    flight_time = ticket['start_time']
    now = timezone.now()
    if flight_date > now.date():
        return True
    elif flight_date == now.date():
        return flight_time > now.time()
    return False


@login_required
def get_user_flights(request, user_flights):
    template_name = 'main/passenger_cabinet.html'
    user = request.user
    tickets = get_user_tickets(user.ticketmodel_set.all())
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'tickets': filter(check_is_user_future_flights, tickets) if user_flights == 'future_flights' else tickets
    }
    return render(request, template_name, context)


@require_http_methods(["GET"])
def get_flights(request, start_location, end_location, start_date, passenger_number):
    flights_query = models.FlightModel.objects.filter(
        start_location=start_location,
        end_location=end_location,
        start_date=start_date
    )
    flights = get_flights_info(flights_query, passenger_number)
    is_flights = False if not flights else True

    context = {
        'flights': flights,
        'is_flights': is_flights,
        'passenger_number': passenger_number
    }
    return render(request, 'main/search_result.html', context)


class IndexView(View):
    template_name = 'main/index.html'

    def get(self, request):
        form = SearchFlightForm()
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SearchFlightForm(request.POST)
        if form.is_valid():
            query_info = {
                'start_location': form.cleaned_data['start_location'],
                'end_location': form.cleaned_data['end_location'],
                'start_date': form.cleaned_data['start_date'],
                'passenger_number': form.cleaned_data['passenger_number']
            }
            return redirect(reverse('main:search_result', kwargs=query_info))

        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class BookView(View):
    template_name = 'main/book_ticket.html'

    def get(self, request, slug_info, start_date, passenger_number, error=None):
        flight = models.FlightModel.objects.get(slug=slug_info)
        seats = get_all_seats(flight)
        flight_info = get_flight_info(flight)
        options = get_flight_options(flight)
        context = {
            'error': error,
            'flight': flight_info,
            'passenger_range': range(passenger_number),
            'seats': seats,
            'options': options
        }
        return render(request, self.template_name, context)

    def post(self, request, slug_info, start_date, passenger_number, error=None):
        flight = models.FlightModel.objects.get(slug=slug_info)
        required_fields = ['First name[]', 'Last name[]', 'email[]']
        try:
            check_post_fields(request, required_fields, passenger_number)
            form = request.POST
            is_form_data_valid(form, passenger_number, flight)
        except ValidationError as e:
            context = {
                'slug_info': slug_info,
                'start_date': start_date,
                'passenger_number': passenger_number,
                'error': e.message
            }
            return redirect(reverse('main:book_ticket_error', kwargs=context))

        total = 0
        for i in range(passenger_number):
            first_name = form.getlist('First name[]')[i]
            last_name = form.getlist('Last name[]')[i]
            email = form.getlist('email[]')[i]
            seat = form.get(f'seat_{i}')
            options = form.getlist(f'options_{i}')

            if not is_user_exist(email):
                user_password = generate_password()
                models.PassengerModel.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=user_password
                )
                context = {
                    'email': email,
                    'password': user_password

                }
                message = render_to_string(
                    'main/email_messages/auto_registration_message.html',
                    context=context
                )
                registration_mail_subject = get_mail_subject('registration', 'Registration')
                send_mail_task.delay(message, email, registration_mail_subject)

            ticket = models.TicketModel.objects.create(
                flight=flight,
                passenger=models.PassengerModel.objects.get(email=email),
                seat=flight.seats.get(seat_number=seat)
            )
            ticket.options.add(*options)
            ticket_context = {
                'start_date': flight.start_date,
                'start_time': flight.start_time,
                'start_location': flight.start_location,
                'end_location': flight.end_location,
                'flight_number': flight.pk,
                'first_name': ticket.passenger.first_name,
                'last_name': ticket.passenger.last_name,
                'seat_number': ticket.seat.seat_number,
                'ticket_number': ticket.pk
            }

            ticket_message = render_to_string(
                'main/email_messages/ticket_info.html',
                context=ticket_context
            )
            ticket_mail_subject = get_mail_subject('ticket', 'Ticket')
            send_mail_task.delay(ticket_message, email, ticket_mail_subject)
            flight_price = flight.price.price
            options_price = get_options_price(ticket.options.all())
            total += options_price + flight_price
            bill_context = {
                'flight_price': flight_price,
                'options_price': options_price,
                'total': options_price + flight_price,
            }
            bill_message = render_to_string(
                'main/email_messages/bill.html',
                bill_context
            )
            bill_mail_subject = get_mail_subject('bill', 'Bill')

            send_mail_task.delay(bill_message, email, bill_mail_subject)
        total = int(total*100)

        return redirect('main:payment', total=total, name=slug_info, amount=passenger_number)


class PaymentView(View):
    try:
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')
        domain_url = getattr(settings, 'DOMAIN_URL')
    except AttributeError:
        raise AttributeError(
            'You must add STRIPE_SECRET_KEY and DOMAIN_URL attributes to your settings'
        )

    def get(self, request, name, total, amount):
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': name,
                    },
                    'unit_amount': total,
                },
                'quantity': amount,
            }],
            mode='payment',
            success_url=self.domain_url + reverse('main:success_payment'),
            cancel_url=self.domain_url + reverse('main:cancel_payment'),
        )
        return redirect(session.url, code=303)


class SuccessPayment(TemplateView):
    template_name = 'main/success_payment.html'


class CancelPayment(TemplateView):
    template_name = 'main/cancel_payment.html'


class LoginView(Login):
    template_name = 'main/login.html'
    redirect_authenticated_user = True
    authentication_form = UserLoginForm


class PassengerCabinetView(View):
    template_name = 'main/passenger_cabinet.html'

    def get(self, request):
        user = request.user
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return render(request, self.template_name, context)


class RegistrationView(View):
    template_name = 'main/registration.html'

    def get(self, request):
        form = RegistrationForm()
        context = {
            'form': form
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            message = render_to_string(
                'main/email_messages/user_registration_message.html',
            )
            registration_mail_subject = get_mail_subject('registration', 'Registration')
            send_mail_task.delay(message, email, registration_mail_subject)

            return redirect('main:cabinet')

        context = {
            'form': form
        }
        return render(request, self.template_name, context)
