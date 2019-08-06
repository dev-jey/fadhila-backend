'''Defines the card type object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import Orders


class OrderType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Orders
        interfaces = (Node, )

class OrdersPaginatedType(graphene.ObjectType):
    count = graphene.Int()
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    items = graphene.List(OrderType)