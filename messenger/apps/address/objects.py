'''Defines the address types object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import County, Town, HomeAddress


class CountyType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = County
        interfaces = (Node, )

class TownType(DjangoObjectType):
    '''Defines the town type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Town
        interfaces = (Node, )

class HomeAddressType(DjangoObjectType):
    '''Defines the town type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = HomeAddress
        interfaces = (Node, )