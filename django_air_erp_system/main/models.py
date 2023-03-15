from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

from .managers import UserManager


class AirplaneModel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(AirplaneModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SeatTypeModel(models.Model):
    class TypeName(models.TextChoices):
        ECONOMY = 'EC', 'Economy class'
        PREMIUM = 'PR', 'Premium economy class'
        BUSINESS = 'BU', 'Business class'
        FIRST = 'FI', 'First class'

    seat_type = models.CharField(
        max_length=2,
        choices=TypeName.choices,
        default=TypeName.ECONOMY
    )

    def __str__(self):
        return self.seat_type


class SeatModel(models.Model):
    seat_type = models.ForeignKey(SeatTypeModel, on_delete=models.CASCADE)
    airplane = models.ForeignKey(AirplaneModel, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField()

    def __str__(self):
        return f'{self.airplane.name}_{self.seat_type}_{self.seat_number}'


class PriceModel(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.price)


class FlightModel(models.Model):
    airplane = models.ForeignKey(AirplaneModel, on_delete=models.CASCADE)
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='flight_prices')
    seats = models.ManyToManyField(SeatModel)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_cancelled = models.BooleanField()
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify([self.start_location, self.end_location])
        super(FlightModel, self).save(*args, **kwargs)

    def __str__(self):
        return f'From {self.start_location} to {self.end_location}'


class PassengerModel(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class OptionModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    flight = models.ForeignKey(FlightModel, on_delete=models.CASCADE, related_name='options')
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='option_prices')

    def __str__(self):
        return self.name


class TicketModel(models.Model):
    flight = models.ForeignKey(FlightModel, on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(PassengerModel, on_delete=models.CASCADE)
    seat = models.ForeignKey(SeatModel, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    options = models.ManyToManyField(OptionModel, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                [self.flight.start_location, self.flight.end_location, self.seat.pk, self.passenger.pk]
            )
        super(TicketModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.flight)


class LuggageModel(models.Model):
    weight = models.FloatField()
    price = models.ForeignKey(PriceModel, on_delete=models.CASCADE, related_name='luggage_prices')
    ticket = models.ForeignKey(TicketModel, on_delete=models.CASCADE, related_name='luggage')

    def __str__(self):
        return str(self.ticket.passenger)


class EmailSubjectModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.name
