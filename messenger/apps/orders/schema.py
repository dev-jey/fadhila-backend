'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from django.db.models import Sum
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import OrderType, OrdersPaginatedType, StatsType
from messenger.apps.authentication.objects import UserType
from .models import Orders, User
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

    @login_required
    def resolve_dashboard_stats(self, info, **kwargs):
        users = User.objects.all().count()
        orders = Orders.objects.filter(is_cancelled=False).count()
        revenue = Orders.objects.filter(is_cancelled=False).aggregate(Sum('total_cost'))['total_cost__sum']
        print(users)
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
        premium = Orders.objects.filter(is_cancelled=False).aggregate(Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
        regular = Orders.objects.filter(is_cancelled=False).aggregate(Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
        total = premium + regular
        transport_costs = Orders.objects.filter(is_cancelled=False).aggregate(Sum('transport_fee'))['transport_fee__sum']
        total_cards_cost = Orders.objects.filter(is_cancelled=False).aggregate(Sum('cost_of_cards'))['cost_of_cards__sum']
        total_revenue = Orders.objects.filter(is_cancelled=False).aggregate(Sum('total_cost'))['total_cost__sum']
        return items_getter_helper(page, orders, OrdersPaginatedType, 
        no_of_premium_batches=premium, no_of_regular_batches=regular,
        total_transport_cost=transport_costs, total_cards_cost=total_cards_cost,
        total_revenue=total_revenue,
        total_no_of_batches=total)


def check_other_filters(kwargs, filter):
    from_date = kwargs.get('from_date', None)
    to = kwargs.get('to', None)
    isCancelled = kwargs.get('is_cancelled')
    orders = None
    if from_date > to:
        raise GraphQLError('Starting date must be less than final date')
    if from_date == to:
        orders = Orders.objects.filter(filter).filter(created_at__date=from_date).filter(is_cancelled=isCancelled).order_by('address__town_name')
    else:
        orders = Orders.objects.filter(filter).filter(created_at__range=(from_date, to)).filter(is_cancelled=isCancelled).order_by('address__town_name')
    return orders
