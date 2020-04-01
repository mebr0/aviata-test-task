from datetime import timedelta, date, datetime

import requests
from celery.task import periodic_task
from django.core.cache import cache

CITIES_1 = ['ALA', 'ALA', 'ALA', 'TSE', 'TSE']  # All pairs of cities
CITIES_2 = ['TSE', 'MOW', 'CIT', 'MOW', 'LED']
FORMAT = '%d/%m/%Y'                             # Date format
LIMIT = 5                                       # Requests limit

FLIGHTS_URI = 'https://api.skypicker.com/flights'
CHECK_URI = 'https://booking-api.skypicker.com/api/v0.1/check_flights'


@periodic_task(run_every=(timedelta(days=1)), name='search_tickets')
def search_tickets():

    today = date.today()
    date_from = today.strftime(FORMAT)

    end = today + timedelta(days=30)
    date_to = end.strftime(FORMAT)

    for first, second in zip(CITIES_1, CITIES_2):
        search_single_direction(first, second, date_from, date_to)
        search_single_direction(second, first, date_from, date_to)


def search_single_direction(fly_from, fly_to, date_from, date_to):
    params = {'fly_from': fly_from, 'fly_to': fly_to, 'date_from': date_from, 'date_to': date_to, 'partner': 'mebr0',
              'curr': 'KZT', 'asc': 1}
    response = requests.get(FLIGHTS_URI, params=params, timeout=120)

    if response.status_code != 200:
        return

    tickets = response.json().get('data')

    if len(tickets) == 0:
        return

    data = {}

    for ticket in tickets:
        current_date = datetime.utcfromtimestamp(ticket.get('dTimeUTC')).strftime(FORMAT)

        key = f'{current_date}_{fly_from}_{fly_to}'

        if data.get(key) is None:

            if check_ticket(ticket.get('booking_token')) != 0:
                break

            data[key] = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

        else:
            their_ticket = data.get(key)

            if their_ticket.get('price') > ticket.get('price'):

                if check_ticket(ticket.get('booking_token')) != 0:
                    break

                data[key] = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

    cache.set('tickets', data, 86400)


def check_ticket(booking_token):
    response = None
    checked = False

    params = {'booking_token': booking_token, 'v': 2, 'partner': 'mebr0', 'bnum': 3, 'pnum': 2,
              'affily': 'picky_market', 'currency': 'KZT'}

    i = 0

    while not checked:
        response = requests.get(CHECK_URI, params=params, timeout=15)
        checked = response.json().get('flights_checked')

        i += 1

        if i >= LIMIT:
            return 1

    invalid = response.json().get('flights_invalid')
    price_change = response.json().get('price_change')

    if invalid:
        return 1

    elif price_change:  # Not implemented :)
        return 2

    return 0
