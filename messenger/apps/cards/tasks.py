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
from .models import Card

from weasyprint import HTML, CSS
from django.core.mail import EmailMessage
from messenger import settings
# from weasyprint import HTML, CSS
# from django.core.mail import EmailMessage


# logger = get_task_logger(__name__)


# @periodic_task(run_every=(crontab(minute='*/1')),
#                name="task_create_random_serials",
#                ignore_result=True)
def task_create_random_serials():
    try:
        order_set = check_available_orders()
        sum_of_regular = order_set.filter(address_id__isnull=True).aggregate(
            Sum('no_of_regular_batches'))['no_of_regular_batches__sum']
        sum_of_premium = order_set.filter(address_id__isnull=True).aggregate(
            Sum('no_of_premium_batches'))['no_of_premium_batches__sum']
        internationals = order_set.filter(address_id__isnull=True)
        for every_order in internationals:
            serials_regular = loop_through_Cards(
                'regular', every_order.no_of_regular_batches)
            serials_premium = loop_through_Cards(
                'premium', every_order.no_of_premium_batches)
            to_email = every_order.owner.email
            send_cards_for_abroad_orders(
                serials_regular, serials_premium, to_email, every_order)
        # logger.info("Created "+str(sum_of_premium+sum_of_regular)+" cards")
        return True
    except BaseException as e:
        # logger.info(e, 'No international orders available')
        print(e)


def check_available_orders():
    '''Get all orders made within the last 24hrs'''
    return Orders.objects.filter(status="S").filter(
        created_at__gte=timezone.now() - timedelta(days=1))


def loop_through_Cards(card_type, no):
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
                card_type='N',
                serial=serial
            )
        card.save()
        serial_numbers.append(card.serial)
    return serial_numbers


def send_cards_for_abroad_orders(serials_regular, serials_premium, to_email, order):
    try:
        html = render_to_string('pdf.html', context={
            'serials_premium': serials_premium, 'serials_regular': serials_regular, 'order': order
        })
        result = HTML(
            string=html, base_url=os.environ['CURRENT_BACKEND_DOMAIN'])
        pdf = result.write_pdf(
            stylesheets=[CSS(settings.STATIC_ROOT + '/css/email.css')], presentational_hints=True, zoom=1.0
        )
        subject = "Fadhila Network Cards Order"
        email = EmailMessage(
            subject, body=pdf, from_email=os.environ['EMAIL_HOST_USER'], to=[to_email])
        email.attach("cards.pdf", pdf, "application/pdf")
        email.content_subtype = "pdf"
        email.encoding = 'us-ascii'
        email.send()
    except Exception as e:
        print(e)
