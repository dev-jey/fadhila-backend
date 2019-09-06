'''Orders app schema'''
import os
import graphene
import uuid
from django.db.models import Q
from django.db.models import Sum
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import OrderType, OrdersPaginatedType, StatsType, CartType
from messenger.apps.authentication.objects import UserType
from messenger.apps.cards.models import Card
from messenger.apps.cards.objects import CardsDataType
from .models import Orders, User, Cart
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
                                search=graphene.String(), is_cancelled=graphene.Boolean(),
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
        orders = Orders.objects.filter(is_cancelled=False).count()
        revenue = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('total_cost'))['total_cost__sum']
        return Stats(users=users, orders=orders, revenue=revenue)

    @login_required
    def resolve_all_orders(self, info, **kwargs):
        '''Resolves all the orders'''
        search = kwargs.get('search', None)
        page = kwargs.get('page', None)
        get_all = kwargs.get('get_all')
        filter = (
            Q(tracking_number__icontains='')
        )
        if search:
            filter = (
                Q(tracking_number__icontains=search)
            )
        orders = check_other_filters(kwargs, filter)
        if get_all:
            orders = Orders.objects.all().order_by('address__town_name')
        premium = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
        regular = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
        transport_costs = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('transport_fee'))['transport_fee__sum']
        total_cards_cost = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('cost_of_cards'))['cost_of_cards__sum']
        total_revenue = Orders.objects.filter(is_cancelled=False).aggregate(
            Sum('total_cost'))['total_cost__sum']
        return items_getter_helper(page, orders, OrdersPaginatedType,
                                   no_of_premium_batches=premium, no_of_regular_batches=regular,
                                   total_transport_cost=transport_costs, total_cards_cost=total_cards_cost,
                                   total_revenue=total_revenue)


def check_other_filters(kwargs, filter):
    from_date = kwargs.get('from_date', None)
    to = kwargs.get('to', None)
    isCancelled = kwargs.get('is_cancelled')
    orders = None
    if from_date > to:
        raise GraphQLError('Starting date must be less than final date')
    if from_date == to:
        orders = Orders.objects.filter(filter).filter(created_at__date=from_date).filter(
            is_cancelled=isCancelled).order_by('address__town_name')
    else:
        orders = Orders.objects.filter(filter).filter(created_at__range=(
            from_date, to)).filter(is_cancelled=isCancelled).order_by('address__town_name')
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
