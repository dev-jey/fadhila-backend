web: gunicorn messenger.wsgi -b 0.0.0.0:$PORT --debug
worker: celery -A messenger worker --loglevel=info --concurrency=1
release: python manage.py migrate