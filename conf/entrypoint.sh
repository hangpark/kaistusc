#!/bin/bash

venv/bin/uwsgi --ini conf/uwsgi.ini
nginx
