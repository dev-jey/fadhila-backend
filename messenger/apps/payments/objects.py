'''Defines the payments type object'''
from graphene import Node
from graphene_django.types import DjangoObjectType
from .models import Payments


class PaymentType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Payments
        interfaces = (Node, )
