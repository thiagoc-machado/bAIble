#!/bin/bash

# Executa as migrações
echo "Executando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Inicia o servidor Gunicorn
echo "Iniciando servidor Gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 