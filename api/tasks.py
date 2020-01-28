import requests

from datetime import timedelta, date, datetime
from celery.task import periodic_task

CITIES = ['ALA', 'MOW', 'TSE', 'LED', 'CIT']
BASE_URI = 'https://api.skypicker.com/flights?fly_from={0}&fly_to={1}&date_from={2}&date_to={3}&partner=mebr0&curr=KZT&asc=1'
D = {}


@periodic_task(run_every=(timedelta(minutes=1)), name='taskA', ignore_result=True)
def do_task():

    start = datetime.now().replace(microsecond=0)

    # for i in range(len(CITIES)):
    #     for j in range(i+1, len(CITIES)):
    #         print('Doing from ' + CITIES[i] + ' to ' + CITIES[j])
    #         do_single_direction(CITIES[i], CITIES[j])

    do_single_direction(CITIES[0], CITIES[1])


    for key in D:
        if D.get(key):
            print(key + ' --- ' + str(D.get(key).get('price')))
        else:
            print(key + ' --- ' + '0')

    end = datetime.now().replace(microsecond=0)

    print(end - start)


def do_single_direction(fly_from, fly_to):
    today = date.today()
    end = today + timedelta(days=30)

    date_from = today.strftime('%d/%m/%Y')
    date_to = end.strftime('%d/%m/%Y')

    for i in range(31):
        D[str(today.strftime('%d/%m/%Y'))] = None

        today += timedelta(days=1)

    do_one_day(fly_from, fly_to, date_from, date_to)


    # for i in range(30):
    #     date_string = today.strftime('%d/%m/%Y')
    #
    #     do_one_day(fly_from, fly_to, date_string)
    #
    #     today += timedelta(days=1)


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

        if D[str(current_date)] == None:
            D[str(current_date)] = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

    # ticket = response.json().get('data')[0]

    # print('date is ' + datetime.utcfromtimestamp(ticket.get('dTimeUTC')).strftime('%d/%m/%Y'))

    # minimum = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

    # print(date_string + ' --- ' + str(minimum.get('price')))
