from graphene_django.types import DjangoObjectType
from .models import User
from graphene import Node


class UserType(DjangoObjectType):

    class Meta:
        model = User
        interfaces = (Node, )
        filter_fields = {
            "username": ["exact", "icontains", "istartswith"]
        }
        exclude_fields=('created_at', 'updated_at','password')