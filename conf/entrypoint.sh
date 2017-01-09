#!/bin/bash

source venv/bin/activate
python kaistusc/manage.py makemigrations
python kaistusc/manage.py migrate
venv/bin/uwsgi --ini conf/uwsgi.ini
nginx
