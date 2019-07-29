'''Defines the card type object'''
from graphene import Node
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
