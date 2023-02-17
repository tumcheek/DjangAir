from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import UserManager


class AirplaneModel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()


class SeatTypeModel(models.Model):
    seat_type = models.CharField(max_length=255)


class SeatModel(models.Model):
    seat_type = models.ForeignKey(SeatTypeModel, on_delete=models.CASCADE)
    airplane = models.ForeignKey(AirplaneModel, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField()


class PriceModel(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)


class FlightModel(models.Model):
    airplane = models.ForeignKey(AirplaneModel, on_delete=models.CASCADE)
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='flight_prices')
    seats = models.ManyToManyField(SeatModel)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    is_cancel = models.BooleanField()
    slug = models.SlugField()


class PassengerModel(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class TicketModel(models.Model):
    flight = models.ForeignKey(FlightModel, on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(PassengerModel, on_delete=models.CASCADE)
    seat = models.ForeignKey(SeatModel, on_delete=models.CASCADE)
    slug = models.SlugField()


class OptionModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    flight = models.ForeignKey(FlightModel, on_delete=models.CASCADE, related_name='options')
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='option_prices')


class LuggageModel(models.Model):
    weight = models.FloatField()
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='luggage_prices')
    ticket = models.ForeignKey(TicketModel, on_delete=models.CASCADE, related_name='luggage')
