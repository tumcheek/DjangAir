import factory
from factory.django import DjangoModelFactory
from ...models import *


class AirplaneFactory(DjangoModelFactory):
    class Meta:
        model = AirplaneModel
    name = factory.Faker('name')


class SeatTypeFactory(DjangoModelFactory):
    class Meta:
        model = SeatTypeModel
    seat_type = factory.Faker('word')


class SeatFactory(DjangoModelFactory):
    class Meta:
        model = SeatModel
    seat_type = factory.SubFactory(SeatTypeFactory)
    airplane = factory.SubFactory(AirplaneFactory)
    seat_number = factory.Faker('pyint')


class PriceFactory(DjangoModelFactory):
    class Meta:
        model = PriceModel
    price = factory.Faker('pydecimal')


class FlightFactory(DjangoModelFactory):
    class Meta:
        model = FlightModel
    airplane = factory.SubFactory(AirplaneFactory)
    price = factory.SubFactory(PriceFactory)
    start_location = factory.Faker('city')
    end_location = factory.Faker('city')
    start_date = factory.Faker('date_time_this_year')
    end_date = factory.Faker('date_time_this_year')
    start_time = factory.Faker('time')
    end_time = factory.Faker('time')
    is_cancel = factory.Faker('pybool')


class PassengerFactory(DjangoModelFactory):
    class Meta:
        model = PassengerModel
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')


class TicketFactory(DjangoModelFactory):
    class Meta:
        model = TicketModel
    flight = factory.SubFactory(FlightFactory)
    passenger = factory.SubFactory(PassengerFactory)
    seat = factory.SubFactory(SeatFactory)
    slug = factory.Faker('slug')


class OptionFactory(DjangoModelFactory):
    class Meta:
        model = OptionModel
    name = factory.Faker('word')
    description = factory.Faker('text')
    flight = factory.SubFactory(FlightFactory)
    price = factory.SubFactory(PriceFactory)


class LuggageFactory(DjangoModelFactory):
    class Meta:
        model = LuggageModel
    weight = factory.Faker('pyfloat')
    price = factory.SubFactory(PriceFactory)
    ticket = factory.SubFactory(TicketFactory)

