import requests

from datetime import timedelta, date
from celery.task import periodic_task

CITIES = ['ALA', 'MOW', 'TSE', 'LED', 'CIT']
BASE_URI = 'https://api.skypicker.com/flights?fly_from={0}&fly_to={1}&date_from={2}&date_to={2}&partner=mebr0&curr=KZT&asc=1'


@periodic_task(run_every=(timedelta(minutes=1)), name='taskA', ignore_result=True)
def do_task():

    for i in range(len(CITIES)):
        for j in range(i+1, len(CITIES)):
            print('Doing from ' + CITIES[i] + ' to ' + CITIES[j])
            do_single_direction(CITIES[i], CITIES[j])


def do_single_direction(fly_from, fly_to):
    today = date.today()

    # date_string = today.strftime('%d/%m/%Y')
    #
    # do_one_day(fly_from, fly_to, date_string)

    for i in range(30):
        date_string = today.strftime('%d/%m/%Y')

        do_one_day(fly_from, fly_to, date_string)

        today += timedelta(days=1)


def do_one_day(fly_from, fly_to, date_string):
    response = requests.get(BASE_URI.format(fly_from, fly_to, date_string))

    if response.status_code != 200:
        print('Not success code! ' + str(response.status_code))
        return

    data = response.json().get('data')

    if len(data) == 0:
        print('Data is empty!')
        return

    ticket = response.json().get('data')[0]

    minimum = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

    print(date_string + ' --- ' + str(minimum.get('price')))
