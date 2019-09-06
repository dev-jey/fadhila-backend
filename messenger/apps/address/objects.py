'''Defines the address types object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import HomeAddress


class HomeAddressType(DjangoObjectType):
    '''Defines the town type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = HomeAddress
        interfaces = (Node, )