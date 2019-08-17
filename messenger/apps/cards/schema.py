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
                               search=graphene.String(), status=graphene.Int(),
                               filters=graphene.Int())

    @login_required
    def resolve_all_cards(self, info, **kwargs):
        '''Resolves all the cards'''
        search = kwargs.get('search', None)
        if search:
            filter = (
                Q(serial__icontains=search)
            )
            cards = Card.objects.filter(filter)
            return cards
        check_other_filters(kwargs)
        cards = Card.objects.filter(
                created_at__gte = timezone.now() - timedelta(days=1))
        return cards
    
def check_other_filters(kwargs):
    status = kwargs.get('status', None)
    filters = kwargs.get('filters', None)
    cards = None
    if status == 2:
        cards = Card.objects.all()
    if status == 0:
        cards = Card.objects.filter(
            created_at__gte = timezone.now() - timedelta(days=30)
        )
    if filters == 2:
        cards = Card.objects.filter(owner__isnull=True)
    if filters == 0:
        cards = Card.objects.filter(
            owner__isnull = False
        )
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
