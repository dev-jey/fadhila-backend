
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import string
import uuid
import os
from graphql import GraphQLError
from datetime import timedelta
from django.utils import timezone

from messenger.apps.orders.models import Orders
from .models import Card


logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute='*/1')),
               name="task_create_random_serials",
               ignore_result=True)
def task_create_random_serials():
    count_of_cards = check_available_orders()
    try:
        stringLength = 6
        for i in range(count_of_cards):
            # get a random string in a UUID fromat
            randomString = uuid.uuid4().hex
            # convert it in a uppercase letter and trim to your size.
            serial = randomString.upper()[0:stringLength]
            card = Card(
                serial=serial
            )
            card.save()
        logger.info("Created "+str(count_of_cards)+" cards")
        return "Created "+str(count_of_cards)+" cards"
    except BaseException as e:
        logger.info(e)


def check_available_orders():
    '''Get all orders made within the last 24hrs'''
    return Orders.objects.filter(
        created_at__gte = timezone.now() - timedelta(days=1)).count()
