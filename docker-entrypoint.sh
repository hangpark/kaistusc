#!/bin/bash

source venv/bin/activate
while ! nc -z db 3306; do sleep 3; done
python manage.py migrate
venv/bin/uwsgi --ini uwsgi.ini
nginx
