import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baible.settings')

app = Celery('baible')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()