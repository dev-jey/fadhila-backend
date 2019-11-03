from django.http import HttpResponse
import os
import uuid
import requests
import datetime
from requests.auth import HTTPBasicAuth
import json
from graphql_extensions.auth.decorators import login_required
from graphql import GraphQLError
import graphene
from .tasks import check_mpesa_confirmation
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential
from django.views.decorators.http import require_http_methods
from messenger.apps.orders.models import Orders, Cart
from .models import Payments
from .objects import PaymentType


@require_http_methods(["POST"])
def confirm_request(request, order_id):
    res = json.loads(request.body)['Body']['stkCallback']['ResultCode']
    new_order = Orders.objects.get(id=order_id)
    confirmation = check_mpesa_confirmation.delay(order_id)
    confirmation.revoke()
    if res != 0:
        new_order.status = 'C'
        new_order.save()
    try:
        my_cart = Cart.objects.get(payer_mobile_no=json.loads(request.body)[
            'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'])
        payment = Payments(
            ref_number=json.loads(request.body)[
                'Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
            amount=json.loads(request.body)[
                'Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
            mobile_no=json.loads(request.body)[
                'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'],
            payment_mode='M',
            paid_at=json.loads(request.body)[
                'Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
            order=new_order,
            owner=new_order.owner
        )
        payment.save()
        my_cart.delete()
        return HttpResponse('Successfully made the payment')
    except Exception as e:
        print(e)
        return HttpResponse('Failure in payment')


class LipaNaMpesa(graphene.Mutation):
    '''Handles payments'''
    # Returns the mpesa success status
    success = graphene.String()

    class Arguments:
        '''Takes in mobile_no and amount details as arguments'''
        mobile_no = graphene.String()
        amount = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        '''Lipa na mpesa mutation'''
        try:
            payer_mobile_no = kwargs.get('mobile_no')
            my_cart = Cart.objects.get(owner=info.context.user)
            my_cart.payer_mobile_no = payer_mobile_no
            my_cart.save()
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = os.environ['MPESA_STKPUSH']
            headers = {"Authorization": "Bearer %s" % access_token}
            tracking_number = uuid.uuid4().hex.upper()[0:8]
            new_order = Orders(
                tracking_number=tracking_number,
                address=my_cart.address,
                receiver_fname=my_cart.receiver_fname,
                receiver_lname=my_cart.receiver_lname,
                mobile_no=payer_mobile_no,
                no_of_regular_batches=my_cart.no_of_regular_batches,
                no_of_premium_batches=my_cart.no_of_premium_batches,
                total_cost=my_cart.total_price,
                owner=my_cart.owner
            )
            new_order.save()
            request = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": kwargs.get('amount'),
                "PartyA": kwargs.get('mobile_no'),
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": kwargs.get('mobile_no'),
                "CallBackURL": f"{os.environ['MPESA_CALLBACK_URL']}/{new_order.id}/",
                "AccountReference": "Fadhila Network",
                "TransactionDesc": "Fadhila Network"
            }
            response = requests.post(api_url, json=request, headers=headers)
            check_mpesa_confirmation.delay(new_order.id)
            return LipaNaMpesa(success=json.loads(response.text)['CustomerMessage'])
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occured. Please try again')



class PaypalPayment(graphene.Mutation):
    '''Paypal payment'''
    # Returns the mpesa success status
    success = graphene.String()

    class Arguments:
        '''Takes in arguments in mutation'''
        order_id = graphene.String()
        payer = graphene.String()
        amount = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        '''Paypal mutation to create order and payment record'''
        try:
            payer = kwargs.get('payer')
            amount = kwargs.get('amount')
            order_id = kwargs.get('order_id')
            my_cart = Cart.objects.get(owner=info.context.user)
            tracking_number = uuid.uuid4().hex.upper()[0:8]
            new_order = Orders(
                tracking_number=tracking_number,
                receiver_fname='',
                receiver_lname='',
                mobile_no='',
                status="S",
                no_of_regular_batches=my_cart.no_of_regular_batches,
                no_of_premium_batches=my_cart.no_of_premium_batches,
                total_cost=my_cart.total_price,
                owner=my_cart.owner
            )
            new_order.save()
            payment = Payments(
            ref_number=order_id,
            amount=amount,
            mobile_no='N/A',
            payment_mode='P',
            paid_at=datetime.datetime.now(),
            order=new_order,
            owner=new_order.owner
            )
            payment.save()
            my_cart.delete()
            return PaypalPayment(success='Payment made successfully')
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occured. Please try again')

class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    lipa_na_mpesa = LipaNaMpesa.Field()
    paypal_payment = PaypalPayment.Field()
