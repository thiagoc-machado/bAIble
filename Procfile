web: sh /app/entrypoint.sh
worker: celery -A baible worker --loglevel=info
beat: celery -A baible beat --loglevel=info