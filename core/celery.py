from __future__ import absolute_import

import os
import sys
import raven,celery

from raven.contrib.celery import register_signal, register_logger_signal

from celery.schedules import crontab
from django.conf import settings


class Celery(celery.Celery):
    def on_configure(self):
        if os.environ.get('RAVEN_ENABLED'):
            client = raven.Client(
                'https://4cf08ac3f077495bbed066c52f50ee61:3169a1e89f0441fca72444c0518382cd@sentry.io/1164181')

            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)

            # hook into the Celery error handler
            register_signal(client)


DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.join(DIR, 'src'))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app = Celery("core")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'send-report-every-single-minute': {
#         'task': 'landing_page.tasks.data_send_to_lc',
#         'schedule': crontab(minute='*/2'),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
#     },
# }