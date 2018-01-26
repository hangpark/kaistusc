#!/bin/bash

source venv/bin/activate
python manage.py migrate
venv/bin/uwsgi --ini uwsgi.ini
nginx
