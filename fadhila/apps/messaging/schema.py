'''Messaging app schema'''
import graphene
from graphene import Node
from graphql import GraphQLError
from graphene_django.filter import DjangoFilterConnectionField
from graphql_extensions.auth.decorators import login_required
from .objects import MessageType
from .models import Message


class Query(graphene.AbstractType):
    '''Defines a query for all messages'''
    def __init__(self):
        pass

    message = Node.Field(MessageType)
    all_messages = DjangoFilterConnectionField(MessageType)

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        '''Resolves all the messages'''
        messages = Message.objects.all()
        if not messages:
            raise GraphQLError("No available messages")
        return messages


class Mutation(graphene.Mutation):
    '''Defines all the messages mutations'''
    message = Node.Field(MessageType)
    class Arguments:
        '''Lists the arguments required 
        in generating cards'''
        no_of_cards = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Define'''
        return 'x'
