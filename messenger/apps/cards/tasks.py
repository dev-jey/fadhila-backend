'''Celry task for processing orders'''
import uuid
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import string
import os
from graphql import GraphQLError
from datetime import timedelta
from django.utils import timezone

from messenger.apps.orders.models import Orders
from django.db.models import Sum
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from messenger.apps.authentication.schema import send_mail
from django.utils import timezone

from .models import Card


logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute='*/10240')),
               name="task_create_random_serials",
               ignore_result=True)
def task_create_random_serials():
    try:
        order_set = check_available_orders()
        sum_of_regular = order_set.filter(address_id__isnull=False).aggregate(
            Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
        sum_of_premium = order_set.filter(address_id__isnull=False).aggregate(
            Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
        loop_through_Cards('regular', sum_of_regular, False)
        loop_through_Cards('premium', sum_of_premium, False)

        internationals = order_set.filter(address_id__isnull=True)
        for every_order in internationals:
            serials_regular = loop_through_Cards('regular', every_order.no_of_regular_batches, True)
            serials_premium = loop_through_Cards('premium', every_order.no_of_premium_batches, True)
            message = render_to_string('send_cards.html', {
                'order': every_order,
                'serials_premium':serials_premium,
                'serials_regular':serials_regular
            })
            mail_subject = 'Here are your cards.'
            to_email = every_order.owner.email
            send_mail(message, mail_subject, to_email)

        logger.info("Created "+str(sum_of_premium+sum_of_regular)+" cards")
        return "Created "+str(sum_of_premium+sum_of_regular)+" cards"
    except BaseException as e:
        logger.info(e)


def check_available_orders():
    '''Get all orders made within the last 24hrs'''
    return Orders.objects.filter(status="S").filter(
        created_at__gte=timezone.now() - timedelta(days=1))

def loop_through_Cards(card_type, no, international):
    stringLength = 6
    serial_numbers = []
    for i in range(no):
        # get a random string in a UUID fromat
        randomString = uuid.uuid4().hex
        # convert it in a uppercase letter and trim to your size.
        serial = randomString.upper()[0:stringLength]
        if card_type == 'premium':
            card = Card(
                card_type='P',
                serial=serial
            )
        if card_type == 'regular':
            card = Card(
                card_type='R',
                serial=serial
            )
        card.save()
        serial_numbers.append(card.serial)
    if international:
        return serial_numbers
