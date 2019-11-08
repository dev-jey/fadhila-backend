web: gunicorn messenger.wsgi
worker: celery -A messenger worker --loglevel=info --concurrency=1
release: python manage.py migrate