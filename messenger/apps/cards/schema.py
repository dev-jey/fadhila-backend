'''Cards app schema'''
import graphene
import uuid
import os
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from .objects import CardType, CardPaginatedType
from messenger.apps.feedback.models import Feedback
from .models import Card, Tracker
from django.template.loader import render_to_string
from .tasks import task_create_random_serials
# from .utils import get_paginator, items_getter_helper



class AllCards(graphene.ObjectType):
    count = graphene.Int()
    cards = graphene.List(CardType)


class Query(graphene.AbstractType):
    '''Defines a query for all cards'''

    def __init__(self):
        pass

    all_cards = graphene.Field(CardPaginatedType, get_all=graphene.Boolean(),
                               search=graphene.String(), owner=graphene.Boolean(),
                               from_date=graphene.String(), to=graphene.String())

    @login_required
    def resolve_all_cards(self, info, **kwargs):
        '''Resolves all the cards'''
        search = kwargs.get('search')
        get_all = kwargs.get('get_all')
        filter = (
            Q(serial__icontains='')
        )
        if search:
            filter = (
                Q(serial__icontains=search)
            )
        cards = check_other_filters(kwargs, filter)
        if get_all:
            cards = Card.objects.all().order_by('owner')
        return AllCards(
            count=cards.count(),
            cards=cards
        )


def check_other_filters(kwargs, filter):
    owner = kwargs.get('owner')
    from_date = kwargs.get('from_date')
    to = kwargs.get('to')
    cards = None
    if from_date > to:
        raise GraphQLError('Starting date must be less than final date')
    if from_date == to:
        return Card.objects.filter(filter).filter(created_at__date=from_date).filter(owner__isnull=owner)
    return Card.objects.filter(filter).filter(created_at__range=(from_date, to)).filter(owner__isnull=owner)




class CreateCard(graphene.Mutation):
    '''Defines all the cards mutations'''
    card = graphene.Field(CardType)

    class Arguments:
        '''Lists the arguments required 
        in generating cards'''
        no_of_regular = graphene.Int()
        no_of_premium = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        '''Generate random x number of cards'''
        try:
            task_create_random_serials()
            stringLength = 6
            card = {}
            no_of_regular = kwargs.get('no_of_regular', None)
            no_of_premium = kwargs.get('no_of_premium', None)
            for i in range(no_of_premium):
                # get a random string in a UUID fromat
                randomString = uuid.uuid4().hex
                # convert it in a uppercase letter and trim to your size.
                serial = randomString.upper()[0:stringLength]
                card = Card(
                    serial=serial,
                    card_type='P'
                )
                card.save()
            for i in range(no_of_regular):
                # get a random string in a UUID fromat
                randomString = uuid.uuid4().hex
                # convert it in a uppercase letter and trim to your size.
                serial = randomString.upper()[0:stringLength]
                card = Card(
                    serial=serial,
                    card_type='N'
                )
                card.save()
            return CreateCard(card=card)
        except BaseException as e:
            print(e)
            raise GraphQLError('Error generating cards', e)


class VerifyCard(graphene.Mutation):
    count = graphene.Int()
    card = graphene.Field(CardType)

    class Arguments:
        serial = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        serial = kwargs.get('serial', None)
        if not serial:
            raise GraphQLError("Enter a serial no")
        try:
            card = Card.objects.get(serial=serial)
            if card.owner is not None and card.owner.email != info.context.user.email:
                return GraphQLError("This card already has an owner")
            if card.owner is not None and card.owner.email == info.context.user.email:
                return GraphQLError("This card has already been saved")
            user = info.context.user.id
            card.owner_id = user
            card.save()
            count = Card.objects.filter(owner=user).count()
            return VerifyCard(card=card, count=count)
        except BaseException as e:
            print(e)
            raise GraphQLError("You have entered an invalid serial number")


class TrackCard(graphene.Mutation):
    count = graphene.Int()
    card = graphene.Field(CardType)

    class Arguments:
        serial = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        serial = kwargs.get('serial', None)
        if not serial:
            return GraphQLError("Enter a serial no")
        try:
            card = Card.objects.get(serial=serial)
        except BaseException as e:
            print(e)
            return GraphQLError("You have entered an invalid serial number")
        if not card.owner:
            return GraphQLError("This card is valid but not registered by the owner to our system yet")
        if card.owner == info.context.user:
            return GraphQLError("This card is registered under your name. Visit your profile to view feedback on this card anytime.")
        feedback_count = Feedback.objects.filter(card=card.id).count()
        if feedback_count == 0:
            return GraphQLError("This card has no feedback yet")
        tracking = Tracker.objects.filter(serial=serial).filter(tracker=info.context.user).count()
        if tracking > 0:
            return GraphQLError("You are already tracking this card. View the feedback on your profile page")
        track_instance = Tracker(
            serial=serial,
            tracker=info.context.user
        )
        track_instance.save()
        return TrackCard(card=card, count=feedback_count)


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    create_card = CreateCard.Field()
    verify_card = VerifyCard.Field()
    track_card = TrackCard.Field()
