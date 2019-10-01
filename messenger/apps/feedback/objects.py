'''Defines the feedback type object'''
from graphene import Node
import graphene
from graphene_django.types import DjangoObjectType
from .models import Feedback


class FeedbackType(DjangoObjectType):
    '''Defines the attributes to be in the type'''
    class Meta:
        '''Specifies some meta data such
         as filtering options'''
        model = Feedback
        interfaces = (Node, )
