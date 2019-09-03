import graphene
from .objects import CountryType
from graphql_extensions.auth.decorators import login_required
from .models import Country

class Query(graphene.AbstractType):
    '''Defines a query for all cards'''
    def __init__(self):
        pass

    all_countries = graphene.List(CountryType)

    @login_required
    def resolve_all_countries(self, info, **kwargs):
        '''Resolves all the countries'''
        countries = Country.objects.all().order_by('name')
        return countries