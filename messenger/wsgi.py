
import os
from django_countries import countries
from messenger.apps.country.models import Country

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')

try:
    for code, name in list(countries):
        Country.objects.get_or_create(name=name, code=code)
except BaseException:
    pass


application = get_wsgi_application()
