#!/usr/bin/env bash
#exit on error
set -0 errexit

#modify this line as needed for your pacakage manager(pip,poetry,etc.)
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate
