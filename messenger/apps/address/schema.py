'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import HomeAddressType
from .models import HomeAddress
from messenger.apps.authentication.objects import UserType


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''
    def __init__(self):
        pass

    all_addresses = graphene.List(HomeAddressType)

    @login_required
    def resolve_all_addresses(self, info):
        addresses = HomeAddress.objects.all()
        return addresses
