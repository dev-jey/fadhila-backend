'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import CountyType
from .models import County
from messenger.apps.authentication.objects import UserType


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''
    def __init__(self):
        pass

    # all_users_by_address = graphene.Field(UserType, town=graphene.Int())
    all_counties = graphene.List(CountyType)

    @login_required
    def resolve_all_counties(self, info):
        '''Resolves all the orders'''
        counties = County.objects.all()
        return counties
