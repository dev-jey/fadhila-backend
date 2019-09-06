'''Defines the user object type'''
import graphene
from graphene import Node
from graphene_django.types import DjangoObjectType
from messenger.apps.country.objects import CountryType
from .models import User


class UserType(DjangoObjectType):
    '''Defines the user type'''
    country = graphene.Field(CountryType)
    class Meta:
        '''Defines the fields to be serialized in the user model'''
        model = User
        interfaces = (Node, )
        filter_fields = {
            "username": ["exact", "icontains", "istartswith"]
        }
        exclude_fields = ('created_at', 'updated_at','password')
