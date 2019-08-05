'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import OrderType, OrdersPaginatedType
from .models import Orders, User
from messenger.apps.cards.utils import get_paginator, items_getter_helper


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''
    def __init__(self):
        pass

    all_orders = graphene.Field(OrdersPaginatedType, page=graphene.Int(),
                               search=graphene.String(), address=graphene.Int(),
                               delivery_status=graphene.Int())

    @login_required
    def resolve_all_orders(self, info, page, address, search=None, delivery_status=None):
        '''Resolves all the orders'''
        if delivery_status is not None:
            orders = Orders.objects.filter(delivery_status=delivery_status)
            return items_getter_helper(page, orders, OrdersPaginatedType)
        if search:
            try:
                user = User.objects.get(username=search)
                filter = (
                    Q(owner=user.id)
                )
                orders = Orders.objects.filter(filter)
                return items_getter_helper(page, orders, OrdersPaginatedType)
            except Exception:
                return GraphQLError("User not found")
        orders = Orders.objects.filter(address=address)
        return items_getter_helper(page, orders, OrdersPaginatedType)
