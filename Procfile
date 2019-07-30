web: gunicorn messenger.wsgi
release: python manage.py migrate && redis-server && celery -A messenger worker -l info && celery -A messenger beat -l info