#!/bin/sh

pytest tests/test_api.py
gunicorn  --workers 4 --bind 0.0.0.0:8000 main:app --reload
