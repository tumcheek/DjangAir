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
