from datetime import datetime
from typing import Union, List, Dict, Any, Tuple
import string
from django.db.models import QuerySet
import stripe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
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

ALLOWED_CHARS = string.ascii_letters + string.digits + string.punctuation


def get_flight_options(flight: models.FlightModel) -> List[Dict[str, Any]]:
    """
    Returns a list of dictionaries containing information about the options available for a given flight.

    Args:
        flight: An instance of a Flight model.

    Returns:
        A list of dictionaries, where each dictionary contains the following information about an option:
            - id: The primary key of the option.
            - name: The name of the option.
            - description: A description of the option.
            - price: The price of the option.
    """
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


def get_flight_info(flight: models.FlightModel) -> Dict[str, Any]:
    """
        Returns a dictionary containing information about a given flight.

        Args:
            flight: An instance of a Flight model.

        Returns:
            A dictionary containing the following information about the flight:
                - start_location: The starting location of the flight.
                - end_location: The ending location of the flight.
                - start_date: The starting date of the flight in 'YYYY-MM-DD' format.
                - end_date: The ending date of the flight in 'YYYY-MM-DD' format.
                - start_time: The starting time of the flight.
                - end_time: The ending time of the flight.
                - slug: The unique slug for the flight.
                - available_seats: The number of available seats on the flight.
                - options: A list of dictionaries containing information about the options available for the flight.
                - price: The price of the flight.
                - is_cancelled: A boolean indicating whether the flight has been cancelled.
        """
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


def get_flights_info(flights_query: Union[QuerySet, List[models.FlightModel]], passengers: int) -> List[Dict[str, Any]]:
    """
    Returns a list of dictionaries containing information about flights that have available seats for a given number of
    passengers.

    Args:
        flights_query: A query set of Flight models.
        passengers: The number of passengers for whom flights are being searched.

    Returns:
        A list of dictionaries, where each dictionary contains the following information about a flight:
            - start_location: The starting location of the flight.
            - end_location: The ending location of the flight.
            - start_date: The starting date of the flight in 'YYYY-MM-DD' format.
            - end_date: The ending date of the flight in 'YYYY-MM-DD' format.
            - start_time: The starting time of the flight.
            - end_time: The ending time of the flight.
            - slug: The unique slug for the flight.
            - available_seats: The number of available seats on the flight.
            - options: A list of dictionaries containing information about the options available for the flight.
            - price: The price of the flight.
            - is_cancelled: A boolean indicating whether the flight has been cancelled.
    """
    flights = []
    for _flight in flights_query:
        flight = get_flight_info(_flight)
        if flight['is_cancelled'] or (flight['available_seats'] - passengers) < 0:
            continue
        flights.append(flight)
    return flights


def get_type_of_seats() -> List[Tuple[str, int]]:
    """
       Returns a list of tuples containing information about the available seat types.

       Args:
           None.

       Returns:
           A list of tuples, where each tuple contains the following information about a seat type:
               - seat_type_display: A string representing the display name of the seat type.
               - pk: The primary key of the seat type.
       """
    _seats_type = models.SeatTypeModel.objects.all()
    seats_type = [(seat_type.get_seat_type_display(), seat_type.pk) for seat_type in _seats_type]
    return seats_type


def get_unavailable_seats(flight: models.FlightModel) -> List[int]:
    """
    Returns a list of seat numbers that are unavailable for a given flight.

    Args:
        flight: A Flight model object.

    Returns:
        A list of integers, where each integer represents a seat number that is unavailable for the given flight.
    """
    flight_tickets = flight.tickets.all()
    tickets_seat = [ticket.seat.seat_number for ticket in flight_tickets]
    return tickets_seat


def get_all_seats(flight: models.FlightModel) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns a dictionary containing information about all the seats on a given flight.

    Args:
        flight: A Flight model object.

    Returns:
        A dictionary where each key represents a seat type, and each value is a list of dictionaries representing seats
        of that type. Each dictionary representing a seat contains the following information:
            - number: The seat number.
            - is_available: A boolean indicating whether the seat is available or not.
    """
    seats_type = get_type_of_seats()
    tickets_seat = get_unavailable_seats(flight)
    seats_dict = {}
    for seat_type, type_pk in seats_type:
        seats = flight.seats.filter(seat_type=type_pk)
        seats_dict[seat_type] = [{'number': seat.seat_number,
                                  'is_available': False if seat.seat_number in tickets_seat else True}
                                 for seat in seats]

    return seats_dict


def check_post_fields(request: HttpRequest, required_fields: List[str], length: int) -> bool:
    """
       Validates that all the required fields are present in the POST request and have the correct length.

       Args:
           request: The Django HTTP request object.
           required_fields: A list of field names that are required in the POST request.
           length: The required length of each field.

       Returns:
           True if all fields are present and have the correct length, otherwise raises a ValidationError.

       Raises:
           ValidationError: If any required field is missing or has the wrong length.
       """
    for field in required_fields:
        if field not in request.POST:
            raise ValidationError(f'Field {field.replace("[]", "")} is required.')
        _field = request.POST.getlist(field)
        if len(_field) != length:
            raise ValidationError(f'Input {field.replace("[]", "")} for all passengers.')
    return True


def is_user_exist(email: str) -> bool:
    """
    Checks if a user exists in the database with the given email.

    Args:
        email: A string representing the email address of the user.

    Returns:
        True if a user with the given email exists in the database, otherwise False.
    """
    user = models.PassengerModel.objects.filter(email=email)
    if user:
        return True
    else:
        return False


def generate_password(length: int = 12, allowed_chars: str = ALLOWED_CHARS) -> str:
    """
    Generates a random password of the specified length.

    Args:
        length: An integer representing the length of the password to generate. Default is 12.
        allowed_chars: : A string containing the characters that can be used in the generated password. Default value
        is a string of all alphanumeric characters and several special characters.
    Returns:
        A string representing the generated password.
    """
    return get_random_string(length=length, allowed_chars=allowed_chars)


def get_mail_subject(name: str, subject: str) -> str:
    """
    Returns the subject of an email by name. If the name is not found in the database,
    the function returns the provided subject.

    Args:
        name (str): The name of the email subject in the database.
        subject (str): The default subject to be returned if the name is not found.

    Returns:
        str: The subject of the email, either from the database or the provided subject.
    """
    try:
        mail_subject = models.EmailSubjectModel.objects.get(name=name).subject
    except ObjectDoesNotExist:
        mail_subject = subject
    return mail_subject


def get_options_price(options: QuerySet) -> float:
    """
    Calculates the total price of a list of flight options.

    Args:
        options (QuerySet): A QuerySet of flight options.

    Returns:
        float: The total price of the flight options.
    """
    _sum = 0
    if options.count() > 0:
        for option in options:
            _sum += option.price.price
    return _sum


def get_ticket_options(options: Union[QuerySet[models.OptionModel], List[models.OptionModel]]) -> List[Dict[str, Any]]:
    """
    Get a list of dictionaries containing information about the options of a ticket.

    Args:
        options: A QuerySet or list of OptionModel objects.

    Returns:
        A list of dictionaries containing the name, description, and price of each option.
    """
    _options = []

    for option in options:
        option_info = {
            'name': option.name,
            'description': option.description,
            'price': option.price.price
        }
        _options.append(option_info)
    return _options


def get_user_tickets(tickets: Union[QuerySet[models.TicketModel], List[models.TicketModel]]) -> List[Dict[str, Any]]:
    """
    Given a queryset of `TicketModel` objects, returns a list of dictionaries representing each ticket with relevant
    information such as the flight's start and end locations, dates, times, the seat's number and type, and any options
    purchased.

    Args:
        tickets: A queryset of `TicketModel` objects representing the tickets to retrieve information for.

    Returns:
        A list of dictionaries, where each dictionary represents a ticket and contains the following keys:
        - "from": A string representing the start location of the flight.
        - "to": A string representing the end location of the flight.
        - "start_date": A string in the format "YYYY-MM-DD" representing the start date of the flight.
        - "end_date": A string in the format "YYYY-MM-DD" representing the end date of the flight.
        - "start_time": A string representing the start time of the flight.
        - "end_time": A string representing the end time of the flight.
        - "seat": A string representing the seat number.
        - "seat_type": A string representing the type of the seat.
        - "options": A list of dictionaries, where each dictionary represents an option purchased and contains the
        following keys:
            - "name": A string representing the name of the option.
            - "description": A string representing the description of the option.
            - "price": A float representing the price of the option.
    """
    _tickets = []
    for ticket in tickets:
        options = get_ticket_options(ticket.options.all())
        ticket_info = {
            'from': ticket.flight.start_location,
            'to': ticket.flight.end_location,
            'start_date': ticket.flight.start_date.strftime('%Y-%m-%d'),
            'end_date': ticket.flight.end_date.strftime('%Y-%m-%d'),
            'start_time': ticket.flight.start_time,
            'end_time': ticket.flight.end_time,
            'seat': ticket.seat.seat_number,
            'seat_type': ticket.seat.seat_type.get_seat_type_display(),
            'options': options
        }
        _tickets.append(ticket_info)
    return _tickets


def check_is_user_future_flights(ticket: Dict[str, Any]) -> bool:
    """
    Check whether the given flight is in the future or not.

    Args:
        ticket: A dictionary containing flight details such as start date and start time.

    Returns:
        A boolean indicating whether the flight is in the future or not.
    """
    flight_date = datetime.strptime(ticket['start_date'], '%Y-%m-%d').date()
    flight_time = ticket['start_time']
    now = timezone.now()
    if flight_date > now.date():
        return True
    elif flight_date == now.date():
        return flight_time > now.time()
    return False


# views that return json
@require_http_methods(["GET"])
def get_location_name(request: HttpRequest) -> JsonResponse:
    """
    View function that returns a JSON response of location names based on the GET parameters 'from', 'to', and 'is_end'.

    Args:
        request: HttpRequest object representing the request made to the server.

    Returns:
        A JsonResponse object containing a list of location names that match the given parameters.
    """
    end_location_query = request.GET.get('to', '')
    start_location_query = request.GET.get('from', '')
    is_end = request.GET.get('is_end', '')
    if is_end:
        end_location = models.FlightModel.objects.filter(
            start_location=start_location_query
        ).filter(end_location__istartswith=end_location_query)
        word_list = [word.end_location for word in end_location]
        return JsonResponse(word_list, safe=False)
    start_location = models.FlightModel.objects.filter(start_location__istartswith=start_location_query)[:3]
    word_list = [word.start_location for word in start_location]
    return JsonResponse(word_list, safe=False)


def book_view_api(request: HttpRequest, slug_info: str, start_date: str) -> JsonResponse:
    """
    Retrieve information about a flight and available seats.

    Args:
        request: The HTTP request object.
        slug_info: A string containing the slug for the flight.
        start_date: A string containing the start date for the flight.

    Returns:
        A JsonResponse object containing a dictionary with the flight information and available seats.
    """
    flight = models.FlightModel.objects.filter(slug=slug_info, start_date=start_date)[0]
    seats = get_all_seats(flight)
    flight_info = get_flight_info(flight)
    context = {
        'flight': flight_info,
        'seats': seats,
    }
    return JsonResponse(context)


# views that return html page
@login_required
def get_user_flights(request: HttpRequest, user_flights: str) -> HttpResponse:
    """
    This function retrieves the user's flight information based on the specified argument.

    Args:
        request (HttpRequest): The HTTP request object.
        user_flights (str): The string argument indicating the type of flights to retrieve.
                             Possible values are: 'future_flights', 'all_flights'.

    Returns:
        HttpResponse: The HTTP response object containing the rendered user flights information.
    """
    template_name = 'main/passenger_cabinet.html'
    user = request.user
    tickets = get_user_tickets(user.ticketmodel_set.all())
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'tickets': filter(check_is_user_future_flights, tickets) if user_flights == 'future_flights' else tickets,
        'is_user_login': True if request.user.is_authenticated else False
    }
    return render(request, template_name, context)


@require_http_methods(["GET"])
def get_flights(
        request: HttpRequest,
        start_location: str,
        end_location: str,
        start_date: str,
        passenger_number: int) -> HttpResponse:
    """
    Get a list of flights that match the specified start location, end location, and start date,
    and render a template with flight information.

    Args:
        request: The HTTP request.
        start_location: The start location of the flight.
        end_location: The end location of the flight.
        start_date: The start date of the flight.
        passenger_number: The number of passengers for the flight.

    Returns:
        An HTTP response with flight information rendered in a template.
    """
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
        'passenger_number': passenger_number,
        'is_user_login': True if request.user.is_authenticated else False
    }
    return render(request, 'main/search_result.html', context)


class IndexView(View):
    """
       Renders the home page of the website with a search form to find flights.
    """
    template_name = 'main/index.html'

    def get(self, request) -> HttpResponse:
        """
        Renders the page with an empty search form.

        Returns:
            HttpResponse: The HTTP response that renders the home page.
        """
        form = SearchFlightForm()
        context = {
            'form': form,
            'is_user_login': True if request.user.is_authenticated else False
        }
        return render(request, self.template_name, context)

    def post(self, request) -> HttpResponse:
        """
        Validates the search form and redirects to the search result page with the search parameters as kwargs.

        Returns:
            HttpResponse: The HTTP response that redirects to the search result page or renders the home page with
            errors if the form is not valid.
        """
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
    """
    View for booking a flight ticket.
    """
    template_name = 'main/book_ticket.html'

    def get(self, request, slug_info: str, start_date: str, passenger_number: int) -> HttpResponse:
        """
        Handles GET requests for the view.

        Args:
            request (HttpRequest): The HTTP request object.
            slug_info (str): The slug of the flight being booked.
            start_date (str): The start date of the flight being booked.
            passenger_number (int): The number of passengers booking tickets.

        Returns:
            HttpResponse: A response containing the rendered HTML template.
        """
        flight = models.FlightModel.objects.get(slug=slug_info)
        flight_info = get_flight_info(flight)
        context = {
            'flight': flight_info,
            'is_user_login': True if request.user.is_authenticated else False,
            'slug_info': slug_info,
            'start_date': start_date,
            'passenger_number': passenger_number
        }
        return render(request, self.template_name, context)

    def post(self, request, slug_info: str, start_date: str, passenger_number: int) -> HttpResponse:
        """
        Handles POST requests for the view.

        Args:
            request (HttpRequest): The HTTP request object.
            slug_info (str): The slug of the flight being booked.
            start_date (str): The start date of the flight being booked.
            passenger_number (int): The number of passengers booking tickets.

        Returns:
            HttpResponse: A redirect response to the payment view or renders the flight book page with
            errors if the form is not valid.
        """
        flight = models.FlightModel.objects.get(slug=slug_info)
        flight_info = get_flight_info(flight)
        required_fields = ['First name[]', 'Last name[]', 'email[]']
        try:
            check_post_fields(request, required_fields, passenger_number)
            form = request.POST
            is_form_data_valid(form, passenger_number, flight)
        except ValidationError as e:
            context = {
                'flight': flight_info,
                'slug_info': slug_info,
                'start_date': start_date,
                'passenger_number': passenger_number,
                'error': e.message,
                'is_user_login': True if request.user.is_authenticated else False
            }
            return render(request, self.template_name, context)

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
    """
    View that handles payments by creating a Stripe checkout session and redirecting the user to the checkout page.

    Attributes:
        stripe.api_key (str): Stripe API secret key.
        domain_url (str): Base URL for the website.
    """
    try:
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')
        domain_url = getattr(settings, 'DOMAIN_URL')
    except AttributeError:
        raise AttributeError(
            'You must add STRIPE_SECRET_KEY and DOMAIN_URL attributes to your settings'
        )

    def get(self, request, name, total, amount):
        """
        HTTP GET method that creates a Stripe checkout session and redirects the user to the checkout page.

        Args:
            request (HttpRequest): The request object used to generate this response.
            name (str): The name of the product.
            total (int): The total price of the product in cents.
            amount (int): The quantity of the product.

        Returns:
            A redirect to the Stripe checkout session URL.
        """
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
    """
    A view that renders the success_payment.html template when a payment is successful.
    """
    template_name = 'main/success_payment.html'


class CancelPayment(TemplateView):
    """
    A view that renders the cancel_payment.html template when a payment is canceled.
    """
    template_name = 'main/cancel_payment.html'


class LoginView(Login):
    """
    View that handles user authentication and login.

    If the user is already authenticated, redirects them to the success URL.

    Parameters:
        template_name (str): The name of the template to use for rendering the login page.
        redirect_authenticated_user (bool): Whether to redirect authenticated users to the success URL.
        authentication_form (class): The form to use for authenticating the user.

    Returns:
        HTTP response: A redirect to the success URL or a rendered login page.
    """
    template_name = 'main/login.html'
    redirect_authenticated_user = True
    authentication_form = UserLoginForm


class PassengerCabinetView(View):
    """
    Renders a template for the passenger cabinet page.
    """
    template_name = 'main/passenger_cabinet.html'

    def get(self, request) -> HttpResponse:
        """
        Handle GET requests to display the passenger cabinet page.

        Parameters:
        - request: the HTTP request object

        Returns:
        - an HTTP response object with the rendered template
        """
        user = request.user
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_user_login': True if request.user.is_authenticated else False
        }
        return render(request, self.template_name, context)


class RegistrationView(View):
    """A view for registering a new user."""
    template_name = 'main/registration.html'

    def get(self, request) -> HttpResponse:
        """Render the registration form."""
        form = RegistrationForm()
        context = {
            'form': form
        }

        return render(request, self.template_name, context)

    def post(self, request) -> HttpResponse:
        """Process the registration form."""
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
