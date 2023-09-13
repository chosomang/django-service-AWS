#!/bin/sh
python manage.py makemigrations
python manage.py migrate --no-input
echo "migrate success"
python manage.py collectstatic --no-input
python manage.py createsuperuser --noinput --username=yoonan --email=yoonan@teiren.io --password=cute428!
gunicorn service.wsgi:application --bind 0.0.0.0:8000
