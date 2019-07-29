
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import string
import uuid
import os
from graphql import GraphQLError

from .models import Card


logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(minute='*/1')), 
                name="task_create_random_serials",
                ignore_result=True)
def task_create_random_serials():
    count_of_cards = check_available_cards()
    if count_of_cards > int(os.environ['MINIMAL_CARDS']):
        logger.info("The available cards are enough")
        return None
    try:
        stringLength = 6
        no_of_cards = int(os.environ['CARDS_PER_GENERATION']) 
        for i in range(no_of_cards):
            # get a random string in a UUID fromat
            randomString = uuid.uuid4().hex
            # convert it in a uppercase letter and trim to your size.
            serial  = randomString.upper()[0:stringLength]
            card = Card(
                serial=serial
            )
            card.save()
        logger.info("Created "+str(no_of_cards)+" cards")
        return card
    except BaseException as e:
        raise GraphQLError('Error generating cards')


def check_available_cards():
    return Card.objects.filter(owner__isnull=True).count()


