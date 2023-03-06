from django.utils.crypto import get_random_string
from .models import PassengerModel, SeatTypeModel


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
        'is_cancel': flight.is_cancel
    }
    return flight_info


def get_flights_info(flights_query, passengers):
    flights = []
    for _flight in flights_query:
        flight = get_flight_info(_flight)
        if flight['is_cancel'] or (flight['available_seats'] - passengers) < 0:
            continue
        flights.append(flight)
    return flights


def get_type_of_seats():
    _seats_type = SeatTypeModel.objects.all()
    seats_type = [(seat_type.seat_type, seat_type.pk) for seat_type in _seats_type]
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
