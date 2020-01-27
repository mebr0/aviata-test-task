import datetime
import requests

from celery.schedules import crontab
from celery.task import periodic_task


@periodic_task(run_every=(datetime.timedelta(seconds=5)), name='taskA', ignore_result=True)
def do_task():
    print('This wasn\'t so difficult')