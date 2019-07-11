import graphene
from graphene import Node
from .objects import MessageType
from .models import Message
from graphql import GraphQLError
from graphene_django.filter import DjangoFilterConnectionField
from graphql_extensions.auth.decorators import login_required


class Query(graphene.AbstractType):
    message = Node.Field(MessageType)
    all_messages = DjangoFilterConnectionField(MessageType)

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        messages = Message.objects.all()
        if not messages:
            raise GraphQLError("No available messages")
        return messages