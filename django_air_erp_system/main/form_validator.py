from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.http import HttpRequest
from .models import FlightModel


def is_seat_available(seat: int, flight: FlightModel) -> bool:
    """
    Check if a seat is available on a given flight.

    Args:
        seat: The seat number to check.
        flight: The flight instance to check the seat availability on.

    Returns:
        A boolean indicating whether the seat is available or not.
    """
    tickets = flight.tickets.all()
    seats = [ticket.seat.seat_number for ticket in tickets]
    if seat in seats:
        return False
    return True


def is_form_data_valid(form: HttpRequest, passenger_number: int, flight: FlightModel) -> bool:
    """
    Validates the form data submitted by the user to book flight tickets.

    Args:
        form: HttpRequest object representing the form data submitted by the user.
        passenger_number: The number of passengers for which tickets are being booked.
        flight: The flight instance for which tickets are being booked.

    Returns:
        bool: True if the form data is valid, False otherwise.

    Raises:
        ValidationError: If any of the input data is invalid.
    """

    first_names = form.getlist('First name[]')
    last_names = form.getlist('Last name[]')
    emails = form.getlist('email[]')

    if '' in first_names or '' in last_names:
        raise ValidationError('Input your First and Last name!')

    seats = set()
    email_validator = EmailValidator()
    for i in range(passenger_number):
        email_validator(emails[i])
        seat_name = f'seat_{i}'
        seat_number = form.get(seat_name, None)
        if seat_number is None:
            raise ValidationError('Pick a seat!')

        if not is_seat_available(int(seat_number), flight):
            raise ValidationError(f'Sorry, but seat {seat_number} is already booked!')

        seats.add(form[seat_name])

    if len(seats) != passenger_number:
        raise ValidationError('Pick seats for each passenger!')

    return True
