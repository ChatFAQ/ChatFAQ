#!/bin/bash
set -e

echo "Apply database migrations"
python manage.py migrate

if [ -v DJANGO_SUPERUSER_PASSWORD ] && [ -v DJANGO_SUPERUSER_USERNAME ] && [ -v DJANGO_SUPERUSER_EMAIL ]
then
    echo "Creating super user"
    {
      python manage.py createsuperuser \
        --noinput \
        --first_name $DJANGO_SUPERUSER_USERNAME \
        --last_name $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL \
        --rpc_group True
    } || {
        echo "Superuser already existed"
    }
fi

echo "Applying fixtures"
make apply_fixtures

if [ "$DEBUG" == "yes" ]
then
    echo "Launching Django DEV..."
    ./manage.py runserver 0.0.0.0:8000
else
    echo "Launching Django PROD..."
    daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
fi
