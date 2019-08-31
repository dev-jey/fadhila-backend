'''Defines the card type object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import Orders
from messenger.apps.cards.objects import CardsDataType


class OrderType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Orders
        interfaces = (Node, )

class OrdersPaginatedType(graphene.ObjectType):
    count = graphene.Int()
    no_of_premium_batches = graphene.Int()
    no_of_regular_batches = graphene.Int()
    total_no_of_batches = graphene.Int()
    total_transport_cost = graphene.Float()
    total_cards_cost = graphene.Float()
    total_revenue = graphene.Float()
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    items = graphene.List(OrderType)

class StatsType(graphene.ObjectType):
    users = graphene.Int()
    revenue = graphene.Int()
    orders = graphene.Int()
