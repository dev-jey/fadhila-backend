web: gunicorn messenger.wsgi
worker: celery -A messenger worker --loglevel=info --concurrency=1 --beat
release: python manage.py migrate