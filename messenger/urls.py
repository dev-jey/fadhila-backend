'''The main project's urls'''
from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from django_countries import countries
from messenger.apps.country.models import Country
# from messenger.apps.payments import schema
from django.conf import settings
from django.conf.urls.static import static
from .views import index

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


try:
    for code, name in list(countries):
        Country.objects.get_or_create(name=name, code=code)
except BaseException:
    pass



urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    # path('mpesa/confirmation/<int:order_id>/', schema.confirm_request, name='mpesa_confirmation'),
    path('graphql', GraphQLView.as_view(graphiql=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)