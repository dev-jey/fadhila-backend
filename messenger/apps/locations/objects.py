'''Defines the location object type'''
from graphene import Node
from graphene_django.types import DjangoObjectType
from .models import Locations


class LocationType(DjangoObjectType):
    '''Defines the locations type'''
    class Meta:
        '''Defines the fields to be serialized in the location model'''
        model = Locations
        interfaces = (Node, )
