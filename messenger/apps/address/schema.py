'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import CountyType, TownType, HomeAddressType
from .models import County, Town, HomeAddress
from messenger.apps.authentication.objects import UserType


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''
    def __init__(self):
        pass

    all_counties = graphene.List(CountyType)
    all_towns = graphene.List(TownType)
    all_addresses = graphene.List(HomeAddressType)

    @login_required
    def resolve_all_counties(self, info):
        '''Resolves all the orders'''
        counties = County.objects.all()
        return counties

    @login_required
    def resolve_all_towns(self, info):
        towns = Town.objects.all()
        return towns

    @login_required
    def resolve_all_addresses(self, info):
        addresses = HomeAddress.objects.all()
        return addresses
