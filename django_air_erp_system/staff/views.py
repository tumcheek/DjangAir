from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import user_passes_test

from .models import BoardingRegistrationModel
from .forms import BoardRegistrationForm
from main.views import check_is_future_flights
from main.models import FlightModel, TicketModel


GROUPS_REDIRECT = {
    'gate_managers': 'staff:gate-manager',
    'check_in_managers': 'staff: check-in-manager',
    'supervisors': 'staff:supervisor'
}


def validate_ticket(ticket_number: int, flight: FlightModel) -> str:
    """
    Validate a ticket for a given flight.

    Args:
        ticket_number (int): The ticket number to validate.
        flight (FlightModel): The flight to check against.

    Returns:
        str: A string indicating the validation result.
    """
    try:
        ticket = TicketModel.objects.select_related('flight').get(id=ticket_number)
    except TicketModel.DoesNotExist:
        return "This ticket does not exist"

    if flight.pk != ticket.flight.pk:
        return "This ticket doesn't match this flight"

    if BoardingRegistrationModel.objects.filter(ticket=ticket).exists():
        return "Ticket has already been registered"

    BoardingRegistrationModel.objects.create(ticket=ticket)
    return "Ticket successfully registered"


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in.

    Args:
        *group_names: A list of group names that the user must be a member of.

    Returns:
        A decorator that can be used to decorate views. The decorated view will
        only be accessible to users who are members of one of the specified
        groups.
    """

    def in_groups(user):
        return user.groups.filter(name__in=group_names).exists() or user.is_superuser

    return user_passes_test(in_groups)


def staff_redirect_view(request: HttpRequest) -> HttpResponse:
    """
    Redirects staff users based on their group membership.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    user = request.user

    for group, redirect_url in GROUPS_REDIRECT.items():
        if user.groups.filter(name=group).exists():
            return redirect(redirect_url)
    return redirect('auth:staff-login')


def get_future_flights(request):
    template_name = 'staff/flights.html'
    flights = list(FlightModel.objects.values())

    context = {
        'flights': list(filter(check_is_future_flights, flights))
    }
    return render(request, template_name, context)


@method_decorator(group_required('gate_managers', 'supervisors'), name='dispatch')
class BoardRegistrationView(View):
    template_name = 'staff/board_registration.html'

    def get(self, request: HttpRequest, flight_slug: str) -> HttpResponse:
        """
        Handle GET request to display the board registration form.

        Args:
            request (HttpRequest): The HTTP request object.
            flight_slug (str): The slug of the flight.

        Returns:
            HttpResponse: The HTTP response object.
        """
        flight = get_object_or_404(FlightModel, slug=flight_slug)
        form = BoardRegistrationForm()
        context = {
            'flight': flight,
            'form': form

        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, flight_slug: str) -> HttpResponse:
        """
        Handle POST request to process the board registration form.

        Args:
            request (HttpRequest): The HTTP request object.
            flight_slug (str): The slug of the flight.

        Returns:
            HttpResponse: The HTTP response object.
        """

        flight = get_object_or_404(FlightModel, slug=flight_slug)
        form = BoardRegistrationForm(request.POST)

        if not form.is_valid():
            message = form.errors
        else:
            ticket_number = form.cleaned_data['ticket_number']
            message = validate_ticket(ticket_number, flight)

        context = {
            'flight': flight,
            'message': message
        }
        return render(request, self.template_name, context)


@method_decorator(group_required('gate_managers'), name='dispatch')
class GateManagerView(View):
    template_name = 'staff/index.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handle GET request to display the gate manager page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        context = {
            'group': 'gate_managers'
        }
        return render(request, self.template_name, context)
