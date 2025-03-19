#!/usr/bin/sh
gunicorn  --workers 4 --bind localhost:8000 main:app --reload
