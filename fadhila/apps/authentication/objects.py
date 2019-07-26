'''Defines the user object type'''
from graphene import Node
from graphene_django.types import DjangoObjectType
from .models import User


class UserType(DjangoObjectType):
    '''Defines the user type'''
    class Meta:
        '''Defines the fields to be serialized in the user model'''
        model = User
        interfaces = (Node, )
        filter_fields = {
            "username": ["exact", "icontains", "istartswith"]
        }
        exclude_fields = ('created_at', 'updated_at','password')
