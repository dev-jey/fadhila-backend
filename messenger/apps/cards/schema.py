'''Cards app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from .objects import CardType, CardPaginatedType
from .models import Card
# from .utils import get_paginator, items_getter_helper


class Query(graphene.AbstractType):
    '''Defines a query for all cards'''
    def __init__(self):
        pass

    all_cards = graphene.List(CardType,
                              search=graphene.String(), owner=graphene.Boolean(),
                              from_date=graphene.String(), to=graphene.String())

    @login_required
    def resolve_all_cards(self, info, **kwargs):
        '''Resolves all the cards'''
        search = kwargs.get('search', None)
        filter = (
                Q(serial__icontains='')
            )
        if search:
            filter = (
                Q(serial__icontains=search)
            )
        cards = check_other_filters(kwargs, filter)
        return cards


def check_other_filters(kwargs, filter):
    owner = kwargs.get('owner')
    from_date = kwargs.get('from_date', None)
    to = kwargs.get('to', None)
    cards = None
    if from_date > to:
        raise GraphQLError('Starting date must be less than final date')
    if from_date == to:
        cards = Card.objects.filter(filter).filter(created_at__date=from_date).filter(owner__isnull=owner)
    else:
        cards = Card.objects.filter(filter).filter(created_at__range=(from_date, to)).filter(owner__isnull=owner)
    return cards


# THIS MUTATION IS NOT IN USE ANY MORE SINCE
# THERE IS A CELERY JOB FOR THIS!!!!!!!!!!!!!!!!


class CreateCard(graphene.Mutation):
    '''Defines all the cards mutations'''
    card = graphene.Field(CardType)

    class Arguments:
        '''Lists the arguments required 
        in generating cards'''
        no_of_cards = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        '''Generate random x number of cards'''
        try:
            stringLength = 6
            no_of_cards = kwargs.get('no_of_cards', None)
            for i in range(no_of_cards):
                # get a random string in a UUID fromat
                randomString = uuid.uuid4().hex
                # convert it in a uppercase letter and trim to your size.
                serial = randomString.upper()[0:stringLength]
                card = Card(
                    serial=serial
                )
                card.save()
            return CreateCard(card=card)
        except BaseException as e:
            raise GraphQLError('Error generating cards', e)


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    # create_card = CreateCard.Field()
