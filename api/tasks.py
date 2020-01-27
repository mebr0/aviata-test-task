from datetime import timedelta, date
import requests

from celery.task import periodic_task

BASE_URI = 'https://api.skypicker.com/flights?fly_from=ALA&fly_to=MOW&date_from={0}&date_to={0}&partner=mebr0&curr=KZT&asc=1'


@periodic_task(run_every=(timedelta(minutes=1)), name='taskA', ignore_result=True)
def do_task():
    delta = timedelta(days=1)
    today = date.today()

    for i in range(30):
        date_string = today.strftime('%d/%m/%Y')

        do_one_day(date_string)

        today += delta


def do_one_day(date_string):
    # print(BASE_URI.format(date_string))

    response = requests.get(BASE_URI.format(date_string))

    if response.status_code != 200:
        print('Not success code! ' + str(response.status_code))
        return

    ticket = response.json().get('data')[0]

    minimum = {'price': ticket.get('price'), 'booking_token': ticket.get('booking_token')}

    print(date_string + ' --- ' + str(minimum.get('price')))
