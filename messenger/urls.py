'''The main project's urls'''
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django_countries import countries
from messenger.apps.country.models import Country



try:
    for code, name in list(countries):
        Country.objects.get_or_create(name=name, code=code)
except BaseException:
    pass



urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql', GraphQLView.as_view(graphiql=True)),
]
