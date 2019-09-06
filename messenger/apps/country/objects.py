'''Defines the user object type'''
from graphene import Node
from graphene_django.types import DjangoObjectType
from .models import Country


class CountryType(DjangoObjectType):
    '''Defines the country type'''
    class Meta:
        '''Defines the fields to be serialized in the country model'''
        model = Country
        interfaces = (Node, )
