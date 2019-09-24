from celery.decorators import task
from celery.utils.log import get_task_logger
from graphql import GraphQLError
from .models import Payments
from messenger.apps.orders.models import Orders

logger = get_task_logger(__name__)


@task(name="check_mpesa_response")
def check_mpesa_confirmation(order_id):
    """checks if mpesa confirmation has been returned"""
    logger.info("Checking for confirmation")
    try:
        exists = Payments.objects.get(order_id=order_id)
        if exists: 
            my_order = Orders.objects.get(id=order_id)
            my_order.status = 'S'
            my_order.save()
            return logger.info("Payment made successfully")
    except BaseException as e:
        logger.info("Not yet reflected")
        check_mpesa_confirmation.s(order_id).apply_async(countdown=60)