from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from .forms import SearchFlightForm
from . import models


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

    def get(self, request, slug_info, start_date, passenger_number):
        flight = models.FlightModel.objects.get(slug=slug_info)
        seats = get_all_seats(flight)
        flight_info = get_flight_info(flight)
        options = get_flight_options(flight)
        context = {
            'flight': flight_info,
            'passenger_range': range(passenger_number),
            'seats': seats,
            'options': options
        }
        return render(request, self.template_name, context)
