import requests

from datetime import timedelta, date, datetime
from celery.task import periodic_task
from djcelery.backends.cache import cache

CITIES = ['ALA', 'MOW', 'TSE', 'LED', 'CIT']
BASE_URI = 'https://api.skypicker.com/flights?fly_from={0}&fly_to={1}&date_from={2}&date_to={3}&partner=mebr0&' \
           'curr=KZT&asc=1'


@periodic_task(run_every=(timedelta(seconds=30)), name='search_tickets')
def do_task():
    start = datetime.now().replace(microsecond=0)

    for i in range(len(CITIES)):
        for j in range(i+1, len(CITIES)):
            print('Doing from ' + CITIES[i] + ' to ' + CITIES[j])
            do_single_direction(CITIES[i], CITIES[j])

    # check single pair of CITIES
    # do_single_direction(CITIES[0], CITIES[1])

    # cache.clear()

    for key in cache.keys('*'):
        print(key + ' --- ' + str(cache.get(key)))

    end = datetime.now().replace(microsecond=0)

    print(str((end - start).seconds) + 's')


def do_single_direction(fly_from, fly_to):
    today = date.today()
    end = today + timedelta(days=30)

    date_from = today.strftime('%d/%m/%Y')
    date_to = end.strftime('%d/%m/%Y')

    do_one_day(fly_from, fly_to, date_from, date_to)


def do_one_day(fly_from, fly_to, date_from, date_to):
    response = requests.get(BASE_URI.format(fly_from, fly_to, date_from, date_to))

    if response.status_code != 200:
        print('Not success code! ' + str(response.status_code))
        return

    data = response.json().get('data')

    if len(data) == 0:
        print('Data is empty!')
        return

    tickets = response.json().get('data')

    for ticket in tickets:
        current_date = datetime.utcfromtimestamp(ticket.get('dTimeUTC')).strftime('%d/%m/%Y')

        if cache.get(str(current_date)) is None:
            cache.set(str(current_date), [])

            listt = cache.get(str(current_date))
            listt.append({'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                          'booking token': ticket.get('booking token')})
            cache.set(str(current_date), listt)

        else:
            their_tickets = cache.get(str(current_date))

            found = False

            for their_ticket in their_tickets:
                if their_ticket.get('from') == fly_from and their_ticket.get('to') == fly_to:

                    found = True

                    if their_ticket.get('price') > ticket.get('price'):
                        their_tickets.remove(their_ticket)

                        their_tickets.append({'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                                              'booking token': ticket.get('booking token')})

                        break

            if not found:
                their_tickets.append({'from': fly_from, "to": fly_to, 'price': ticket.get('price'),
                                      'booking token': ticket.get('booking token')})

            cache.set(str(current_date), their_tickets)
