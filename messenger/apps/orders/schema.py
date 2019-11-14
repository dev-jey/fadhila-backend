'''Orders app schema'''
import os
import graphene
from django.db.models import Q
from django.db.models import Sum
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import OrderType, OrdersPaginatedType, StatsType, CartType
from messenger.apps.authentication.objects import UserType
from messenger.apps.cards.models import Card
from messenger.apps.cards.objects import CardsDataType
from .models import Orders, User, Cart, Locations
from messenger.apps.cards.utils import get_paginator, items_getter_helper


class Stats(graphene.ObjectType):
    users = graphene.Int()
    orders = graphene.Int()
    revenue = graphene.Int()


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''

    def __init__(self):
        pass

    all_orders = graphene.Field(OrdersPaginatedType, page=graphene.Int(), get_all=graphene.Boolean(),
                                search=graphene.String(), status=graphene.String(), foreign=graphene.Boolean(),
                                from_date=graphene.String(), to=graphene.String()
                                )
    dashboard_stats = graphene.Field(StatsType)

    current_user_cards = graphene.Field(CardsDataType, page=graphene.Int())

    current_user_orders = graphene.Field(
        OrdersPaginatedType, page=graphene.Int())

    get_cart = graphene.Field(CartType)

    @login_required
    def resolve_get_cart(self, info, **kwargs):
        current_user = info.context.user.id
        try:
            cart = Cart.objects.get(owner=current_user)
            return cart
        except BaseException as e:
            new_cart = Cart(no_of_regular_batches=0,
                            no_of_premium_batches=0,
                            price_of_regular=0,
                            price_of_premium=0,
                            total_price=0,
                            owner=info.context.user)
            new_cart.save()
            return new_cart

    @login_required
    def resolve_current_user_cards(self, info, **kwargs):
        page = kwargs.get('page')
        current_user = info.context.user.id
        try:
            cards = Card.objects.filter(owner_id=current_user)
            return items_getter_helper(page, cards, CardsDataType)
        except BaseException as e:
            print(e)
            raise GraphQLError("An error occured while fetching cards")

    @login_required
    def resolve_current_user_orders(self, info, **kwargs):
        page = kwargs.get('page')
        current_user = info.context.user.id
        try:
            orders = Orders.objects.filter(owner_id=current_user)
            return items_getter_helper(page, orders, OrdersPaginatedType)
        except BaseException as e:
            print(e)
            raise GraphQLError("An error occured while fetching orders")

    @login_required
    def resolve_dashboard_stats(self, info, **kwargs):
        users = User.objects.all().count()
        orders = Orders.objects.count()
        revenue = Orders.objects.filter(status='S').aggregate(
            Sum('total_cost'))['total_cost__sum']
        return Stats(users=users, orders=orders, revenue=revenue)

    @login_required
    def resolve_all_orders(self, info, **kwargs):
        '''Resolves all the orders'''
        search = kwargs.get('search', None)
        page = kwargs.get('page', None)
        get_all = kwargs.get('get_all')
        status = kwargs.get('status', None)
        foreign = kwargs.get('foreign')
        if not foreign:
            foreign = False
        from_date = kwargs.get('from_date', None)
        to = kwargs.get('to', None)
        filter = (
            Q(tracking_number__icontains='')
        )
        if search:
            filter = (
                Q(tracking_number__icontains=search)
            )
        orders = check_other_filters(kwargs, filter, foreign)

        if from_date == to:
            premium = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__range=(
                from_date, to)).aggregate(
                Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
            regular = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__range=(
                from_date, to)).aggregate(
                Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
            total_cards_cost = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__date=to).aggregate(
                Sum('total_cost'))['total_cost__sum']
        if from_date < to:
            premium = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__range=(
                from_date, to)).aggregate(
                Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
            regular = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__range=(
                from_date, to)).aggregate(
                Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
            total_cards_cost = Orders.objects.filter(status=status).filter(address__isnull=foreign).filter(filter).filter(created_at__range=(
                from_date, to)).aggregate(
                Sum('total_cost'))['total_cost__sum']

        if get_all:
            premium = Orders.objects.aggregate(
                Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
            regular = Orders.objects.aggregate(
                Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
            total_cards_cost = Orders.objects.aggregate(
                Sum('total_cost'))['total_cost__sum']
            orders = Orders.objects.all().order_by('address')

        return items_getter_helper(page, orders, OrdersPaginatedType,
                                   no_of_premium_batches=premium, no_of_regular_batches=regular,
                                   total_cards_cost=total_cards_cost)


def check_other_filters(kwargs, filter, foreign):
    from_date = kwargs.get('from_date', None)
    to = kwargs.get('to', None)
    status = kwargs.get('status')
    orders = None
    if from_date > to:
        raise GraphQLError('Starting date must be less than final date')
    if from_date == to:
        orders = Orders.objects.filter(filter).filter(address__isnull=foreign).filter(
            created_at__date=from_date).filter(status=status).order_by('address')
    else:
        orders = Orders.objects.filter(filter).filter(address__isnull=foreign).filter(created_at__range=(
            from_date, to)).filter(status=status).order_by('address')
    return orders


class AddToCart(graphene.Mutation):
    '''Adds to the cart'''
    # Returns the cart instance info
    cart = graphene.Field(CartType)

    class Arguments:
        '''Takes in cart details as arguments'''
        status = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        '''Add to cart mutation'''
        status = kwargs.get('status', None)
        try:
            owner = info.context.user
            existing_cart = Cart.objects.get(owner=owner)
            if status == 0:
                existing_cart.no_of_regular_batches += 1
                return AddToCart(cart=calculate_totals(existing_cart))
            if status == 1:
                existing_cart.no_of_premium_batches += 1
                return AddToCart(cart=calculate_totals(existing_cart))

            if status == 2:
                existing_cart.no_of_regular_batches -= 1
                return AddToCart(cart=calculate_totals(existing_cart))

            existing_cart.no_of_premium_batches -= 1
            return AddToCart(cart=calculate_totals(existing_cart))

        except Exception as e:
            print(e)
            raise GraphQLError('There has been an error updating your cart')


class UpdateCart(graphene.Mutation):
    '''Update the Cart Details'''
    # Returns the cart instance info
    cart = graphene.Field(CartType)

    class Arguments:
        '''Takes in cart details as arguments'''
        receiver_fname = graphene.String()
        receiver_lname = graphene.String()
        address = graphene.String()
        mobile_no = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Add to cart mutation'''
        try:
            owner = info.context.user
            location_id = Locations.objects.get(
                name=kwargs.get('address').strip())
            existing_cart = Cart.objects.get(owner=owner)
            existing_cart.receiver_fname = kwargs.get(
                'receiver_fname', None).strip()
            existing_cart.receiver_lname = kwargs.get(
                'receiver_lname', None).strip()
            existing_cart.address = location_id
            existing_cart.mobile_no = kwargs.get('mobile_no')
            existing_cart.save()
            return UpdateCart(cart=existing_cart)
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occurred in saving your credentials')


def calculate_totals(existing_cart):
    existing_cart.price_of_regular = int(os.environ['PRICE_OF_REGULAR']) * \
        existing_cart.no_of_regular_batches
    existing_cart.price_of_premium = int(os.environ['PRICE_OF_PREMIUM']) * \
        existing_cart.no_of_premium_batches
    existing_cart.total_price = existing_cart.price_of_regular + \
        existing_cart.price_of_premium
    existing_cart.save()
    return existing_cart


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    add_to_cart = AddToCart.Field()
    update_cart = UpdateCart.Field()
