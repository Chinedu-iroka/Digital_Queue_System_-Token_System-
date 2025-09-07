import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Queue_System.settings')

app = Celery('Digital_Queue_System')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()