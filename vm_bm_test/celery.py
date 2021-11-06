from __future__ import absolute_import, unicode_literals

import sys

from celery import Celery
import os
# from note import tasks
sys.path.append(os.path.abspath('vm_bm_test'))
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vm_bm_test.settings')

app = Celery('vm_bm_test')
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'vm_bm.tasks.json_adaptor_process',
        'schedule': 30.0,
    },
}
# from __future__ import absolute_import
# import os
# from celery import Celery
# from django.conf import settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','vm_bm_test.settings')
# app = Celery('vm_bm_test')
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)