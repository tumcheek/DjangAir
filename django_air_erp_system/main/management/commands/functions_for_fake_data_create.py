import random

from .factories import *
from ...models import *


def delete_all_data():
    AirplaneModel.objects.all().delete()
    SeatTypeModel.objects.all().delete()
    SeatModel.objects.all().delete()
    PriceModel.objects.all().delete()
    FlightModel.objects.all().delete()
    PassengerModel.objects.all().delete()
    TicketModel.objects.all().delete()
    OptionModel.objects.all().delete()
    LuggageModel.objects.all().delete()


def create_fake_airplanes(num_airplanes):
    airplanes = []
    for _ in range(num_airplanes):
        airplane = AirplaneFactory()
        airplanes.append(airplane)
    return airplanes


def create_fake_seats_type(seat_types_names):
    seat_types = []
    for seat_type_name in seat_types_names:
        seat_type = SeatTypeFactory(seat_type=seat_type_name)
        seat_types.append(seat_type)
    return seat_types


def create_fake_seats(seat_numbers, seat_types, airplanes):
    seats = []
    for airplane in airplanes:
        for i in range(1, seat_numbers + 1):
            seat = SeatFactory(
                seat_number=i,
                seat_type=random.choice(seat_types),
                airplane=airplane
            )
            seats.append(seat)
    return seats


def create_fake_prices(num_prices, prices_list):
    prices = []
    for _ in range(num_prices):
        price = PriceFactory(price=random.choice(prices_list))
        prices.append(price)
    return prices


def create_fake_flights(num_flights, airplanes, prices):
    flights = []
    for airplane in airplanes:
        for _ in range(num_flights):
            flight = FlightFactory(
                airplane=airplane,
                price=random.choice(prices),
            )
            airplane_seats = [seat.id for seat in airplane.seats.all()]
            flight.seats.add(*airplane_seats)
            flights.append(flight)
    return flights


def create_fake_passengers(num_passengers, password):
    passengers = []
    for _ in range(num_passengers):
        passenger = PassengerFactory(password=password)
        passengers.append(passenger)
    return passengers


def create_fake_tickets(num_tickets, passengers, flights, seats):
    tickets = []
    for _ in range(num_tickets):
        ticket = TicketFactory(
            passenger=random.choice(passengers),
            flight=random.choice(flights),
            seat=random.choice(seats)
        )
        tickets.append(ticket)
    return tickets


def create_fake_options(num_options, flights, prices):
    options = []
    for _ in range(num_options):
        option = OptionFactory(
            flight=random.choice(flights),
            price=random.choice(prices)
        )
        options.append(option)
    return options


def create_fake_luggages(num_luggage, tickets, prices):
    luggages = []
    for _ in range(num_luggage):
        luggage = LuggageFactory(
            ticket=random.choice(tickets),
            price=random.choice(prices)
        )
        luggages.append(luggage)
    return luggages
