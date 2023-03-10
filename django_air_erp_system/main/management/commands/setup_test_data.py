import random
from django.db import transaction
from django.core.management.base import BaseCommand

from . import fake_data_creator as data_creator


NUM_AIRPLANES = 25
SEAT_TYPES_NAMES = ['Economy class', 'Premium economy class', 'Business class', 'First class']
SEAT_NUMBERS = 100
NUM_PRICES = 25
PRICES_LIST = [round(random.random() * 100, 2) for i in range(10)]
NUM_FLIGHTS = 25
NUM_PASSENGERS = 20
NUM_TICKETS = 100
NUM_OPTIONS = 25
NUM_LUGGAGE = 25


class Command(BaseCommand):
    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")

        data_creator.delete_all_data()
        airplanes = data_creator.create_fake_airplanes(NUM_AIRPLANES)
        seat_types = data_creator.create_fake_seats_type(SEAT_TYPES_NAMES)
        seats = data_creator.create_fake_seats(SEAT_NUMBERS, seat_types, airplanes)
        prices = data_creator.create_fake_prices(NUM_PRICES, PRICES_LIST)
        flights = data_creator.create_fake_flights(NUM_FLIGHTS, airplanes, prices)
        passengers = data_creator.create_fake_passengers(NUM_PASSENGERS, 'password')
        tickets = data_creator.create_fake_tickets(NUM_TICKETS, passengers, flights, seats)
        data_creator.create_fake_options(NUM_OPTIONS, flights, prices)
        data_creator.create_fake_luggages(NUM_LUGGAGE, tickets, prices)
