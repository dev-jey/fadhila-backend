'''Defines the message type object'''
from graphene import Node
from graphene_django.types import DjangoObjectType
from .models import Message


class MessageType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Message
        interfaces = (Node, )
        filter_fields = {
            "title": ["icontains", "istartswith"],
            "content":["icontains", "istartswith"],
            "created_at":["exact"]
        }
