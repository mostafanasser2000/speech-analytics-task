#!/usr/bin/sh
uwsgi --http :8000 --wsgi-file main.py --callable app --processes 4 --threads 2
