#!/usr/bin/env bash

# Try to migrating the DB
python manage.py check
python manage.py migrate


# Run web in dev mode
python manage.py runserver 0.0.0.0:8080

