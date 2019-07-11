import graphene
from graphene import Node
from .objects import MessageType
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.AbstractType):
    message = Node.Field(MessageType)
    all_messages = DjangoFilterConnectionField(MessageType)