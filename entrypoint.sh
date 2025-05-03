#!/bin/bash

echo "Executando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
# python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn..."
exec gunicorn baible.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
