web: python manage.py migrate && gunicorn Digital_Queue_System.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A Digital_Queue_System worker --loglevel=info