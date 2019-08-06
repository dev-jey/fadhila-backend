'''Orders app schema'''
import graphene
import uuid
from django.db.models import Q
from graphql import GraphQLError
from graphql_extensions.auth.decorators import login_required
from .objects import OrderType, OrdersPaginatedType
from messenger.apps.authentication.objects import UserType
from .models import Orders, User
from messenger.apps.cards.utils import get_paginator, items_getter_helper


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''
    def __init__(self):
        pass

    # all_users_by_address = graphene.Field(UserType, town=graphene.Int())
    all_orders = graphene.Field(OrdersPaginatedType, page=graphene.Int(),
                               search=graphene.String(), town=graphene.Int(),
                               delivery_status=graphene.Int())
    

    # @login_required
    # def resolve_all_users_by_address(self, info, town):
    #     '''Resolves all users by address'''
    #     if town:
    #         orders = Orders.objects.filter(town=town)
    #         if not orders:
    #             return GraphQLError("There are no orders from this region yet")
    #         return orders
    #     orders = Orders.objects.all()
    #     for order in orders:
    #         return order.owner

    @login_required
    def resolve_all_orders(self, info, page, town=None, search=None, delivery_status=None):
        '''Resolves all the orders'''
        if town:
            orders = Orders.objects.filter(town=town)
            return items_getter_helper(page, orders, OrdersPaginatedType)
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
        orders = Orders.objects.filter(town=town)
        return items_getter_helper(page, orders, OrdersPaginatedType)
