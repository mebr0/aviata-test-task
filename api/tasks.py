import requests

from datetime import timedelta, date, datetime
from celery.task import periodic_task
from djcelery.backends.cache import cache

CITIES = ['ALA', 'MOW', 'TSE', 'LED', 'CIT']
FORMAT = '%d/%m/%Y'
LIMIT = 5

BASE_URI_FLIGHTS = 'https://api.skypicker.com/flights?fly_from={0}&fly_to={1}&date_from={2}&date_to={3}&partner=mebr0&' \
                   'curr=KZT&asc=1'
BASE_URI_CHECK = 'https://booking-api.skypicker.com/api/v0.1/check_flights?v=2&booking_token={0}&partner=mebr0&bnum=3&p' \
                 'num=2&affily=picky_market&currency=KZT'


@periodic_task(run_every=(timedelta(minutes=9)), name='search_tickets')
def search_tickets():
    cache.clear()

    start = datetime.now().replace(microsecond=0)

    for i in range(len(CITIES)):
        for j in range(i + 1, len(CITIES)):
            print('Doing from ' + CITIES[i] + ' to ' + CITIES[j])
            search_single_direction(CITIES[i], CITIES[j])

    # for key in cache.keys('*'):
    #     print(key + ' --- ' + str(cache.get(key)))

    end = datetime.now().replace(microsecond=0)

    print(str(end - start))


def search_single_direction(fly_from, fly_to):
    today = date.today()
    date_from = today.strftime(FORMAT)

    end = today + timedelta(days=30)
    date_to = end.strftime(FORMAT)

    search_single_direction_dates(fly_from, fly_to, date_from, date_to)


def search_single_direction_dates(fly_from, fly_to, date_from, date_to):
    response = requests.get(BASE_URI_FLIGHTS.format(fly_from, fly_to, date_from, date_to))

    if response.status_code != 200:
        print('Not success code! ' + str(response.status_code))
        return

    data = response.json().get('data')

    if len(data) == 0:
        print('Data is empty!')
        return

    tickets = response.json().get('data')

    for ticket in tickets:
        current_date = datetime.utcfromtimestamp(ticket.get('dTimeUTC')).strftime(FORMAT)

        if cache.get(str(current_date)) is None:

            if check_ticket(ticket.get('booking_token')) != 0:
                break

            their_tickets = [{'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                              'booking_token': ticket.get('booking_token')}]
            cache.set(str(current_date), their_tickets)

        else:
            their_tickets = cache.get(str(current_date))

            found = False

            for their_ticket in their_tickets:
                if their_ticket.get('from') == fly_from and their_ticket.get('to') == fly_to:

                    found = True

                    if their_ticket.get('price') > ticket.get('price'):

                        if check_ticket(ticket.get('booking_token')) != 0:
                            break

                        their_tickets.remove(their_ticket)

                        their_tickets.append({'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                                              'booking_token': ticket.get('booking_token')})

                        break

            if not found and check_ticket(ticket.get('booking_token')) == 0:
                their_tickets.append({'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                                      'booking_token': ticket.get('booking_token')})

            cache.set(str(current_date), their_tickets)


def check_ticket(booking_token):
    response = None
    checked = False

    i = 0

    while not checked:
        response = requests.get(BASE_URI_CHECK.format(booking_token))
        checked = response.json().get('flights_checked')

        i += 1

        if i >= LIMIT:
            return 1

    data = response.json()

    print("Checking! " + booking_token[:10])

    invalid = data.get('flights_invalid')
    price_change = data.get('price_change')

    if invalid:
        return 1
    # Not implemented :)
    elif price_change:
        return 2

    return 0
