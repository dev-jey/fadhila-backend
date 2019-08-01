'''Cards app schema'''
import graphene
import uuid
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import CardType, CardPaginatedType
from .models import Card
from .utils import get_paginator


class Query(graphene.AbstractType):
    '''Defines a query for all cards'''
    def __init__(self):
        pass

    all_cards = graphene.Field(CardPaginatedType, page=graphene.Int())

    @login_required
    def resolve_all_cards(self, info, page):
        '''Resolves all the cards'''
        cards = Card.objects.all()
        count = cards.count()
        page_size = 30
        return get_paginator(cards, count, page_size, page, CardPaginatedType)

#THIS MUTATION IS NOT IN USE ANY MORE SINCE
#THERE IS A CELERY JOB FOR THIS!!!!!!!!!!!!!!!!
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
            no_of_cards = kwargs.get('no_of_cards')
            for i in range(no_of_cards):
                # get a random string in a UUID fromat
                randomString = uuid.uuid4().hex
                # convert it in a uppercase letter and trim to your size.
                serial  = randomString.upper()[0:stringLength]
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
