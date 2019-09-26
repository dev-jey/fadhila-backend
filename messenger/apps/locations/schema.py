import graphene
from .objects import LocationType
from graphql import GraphQLError
from django.db.models import Q
from graphql_extensions.auth.decorators import login_required
from .models import Locations

class Query(graphene.AbstractType):
    '''Defines a query for all locations'''
    def __init__(self):
        pass

    all_locations = graphene.List(LocationType, search=graphene.String())

    @login_required
    def resolve_all_locations(self, info, **kwargs):
        '''Resolves all the locations'''
        search = kwargs.get('search', None)
        filter = (
            Q(name='')
        )
        if search:
            filter = (
                Q(name__icontains=search)
            )
        locations = Locations.objects.filter(filter).order_by('name')
        return locations