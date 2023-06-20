from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import user_passes_test

from .models import BoardingRegistrationModel
from .forms import BoardRegistrationForm, StaffRegistrationForm
from main.views import check_is_future_flights, is_user_exist
from main.models import FlightModel, TicketModel, PassengerModel


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


@group_required(*GROUPS_REDIRECT.keys())
def get_future_flights(request: HttpRequest, group: str) -> HttpResponse:
    """
    Retrieves future flights and renders them in a template.

    Args:
        request (HttpRequest): The HTTP request object.
        group (str): The group parameter.

    Returns:
        HttpResponse: The rendered response.

    """
    template_name = 'staff/flights.html'
    flights = list(FlightModel.objects.values())

    context = {
        'flights': list(filter(check_is_future_flights, flights)),
        'group': group,
        'is_user_login': True if request.user.is_authenticated else False
    }
    return render(request, template_name, context)


@group_required('supervisors')
def cancel_flights(request: HttpRequest, group: str, flight_slug: str) -> HttpResponse:
    """
    Cancels flights with the given flight_slug.

    Args:
        request (HttpRequest): The HTTP request object.
        group (str): The group parameter.
        flight_slug (str): The slug of the flight to be cancelled.

    Returns:
        HttpResponse: The redirect response to the staff flights page.

    """
    FlightModel.objects.filter(slug=flight_slug).update(is_cancelled=True)
    return redirect('staff:flights', group)


@group_required('supervisors')
def uncancel_flights(request: HttpRequest, group: str, flight_slug: str) -> HttpResponse:
    """
    Uncancels flights with the given flight_slug.

    Args:
        request (HttpRequest): The HTTP request object.
        group (str): The group parameter.
        flight_slug (str): The slug of the flight to be uncanceled.

    Returns:
        HttpResponse: The redirect response to the staff flights page.

    """
    FlightModel.objects.filter(slug=flight_slug).update(is_cancelled=False)
    return redirect('staff:flights', group)


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
            'group': 'gate_managers',
            'is_user_login': True if request.user.is_authenticated else False
        }
        return render(request, self.template_name, context)


@method_decorator(group_required('supervisors'), name='dispatch')
class SupervisorView(View):
    template_name = 'staff/index.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handle GET request to display the supervisor page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        context = {
            'group': 'supervisors',
            'is_user_login': True if request.user.is_authenticated else False
        }
        return render(request, self.template_name, context)


class StaffRegistrationView(View):
    template_name = 'staff/register_staff.html'

    def get(self, request, group: str) -> HttpResponse:
        """
        Handles GET requests for staff registration.

        Args:
            request (HttpRequest): The HTTP request object.
            group (str): The group parameter.

        Returns:
            HttpResponse: The rendered response.

        """
        form = StaffRegistrationForm
        context = {
            'form': form,
            'group': group
        }

        return render(request, self.template_name, context)

    def post(self, request, group: str) -> HttpResponse:
        """
        Handles POST requests for staff registration.

        Args:
            request (HttpRequest): The HTTP request object.
            group (str): The group parameter.

        Returns:
            HttpResponse: The rendered response.

        """
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            group_name = form.cleaned_data['group']
            _group = Group.objects.get(name=group_name)

            if is_user_exist(email):
                user = PassengerModel.objects.get(email=email)
                user.is_staff = True
                user.save()
            else:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                password = form.cleaned_data['password']

                user = PassengerModel.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                    is_staff=True
                )

            user.groups.add(_group)
            context = {
                'form': StaffRegistrationForm(),
                'group': group
            }
            return render(request, self.template_name, context)

        context = {
            'form': form,
            'group': group
        }
        return render(request, self.template_name, context)
