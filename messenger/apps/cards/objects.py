'''Defines the card type object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import Card


class CardType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Card
        interfaces = (Node, )
        filter_fields = {
            "owner": ["exact"],
            "serial": ["icontains", "istartswith"],
            "created_at":["exact"],
            "updated_at":["exact"]
        }

class CardPaginatedType(graphene.ObjectType):
    count = graphene.Int()
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    cards = graphene.List(CardType)
