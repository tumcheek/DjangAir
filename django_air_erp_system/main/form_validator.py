from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


def is_seat_available(seat, flight):
    tickets = flight.tickets.all()
    seats = [ticket.seat.seat_number for ticket in tickets]
    if seat in seats:
        return False
    return True


def is_form_data_valid(form, passenger_number, flight):

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
