from graphene_django.types import DjangoObjectType
from .models import Message
from graphene import Node

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        interfaces = (Node, )
        filter_fields = {
            "title": ["icontains", "istartswith"],
            "content":["icontains", "istartswith"],
            "created_at":["exact"]
        }
