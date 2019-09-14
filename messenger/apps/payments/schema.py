from django.http import HttpResponse
import os
import uuid
import requests
from requests.auth import HTTPBasicAuth
import json
from graphql_extensions.auth.decorators import login_required
from graphql import GraphQLError
import graphene
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential
from django.views.decorators.http import require_http_methods
from messenger.apps.orders.models import Orders, Cart
from .models import Payments
from .objects import PaymentType


class Query(graphene.AbstractType):
    '''Defines a query for all orders'''

    def __init__(self):
        pass

    check_paid = graphene.Field(PaymentType)

    @login_required
    def resolve_check_paid(self, info, **kwargs):
        current_user = info.context.user
        try:
            exists = Payments.objects.get(owner=current_user)
            return exists
        except BaseException as e:
            raise GraphQLError('Error in retrieving payment')

@require_http_methods(["POST"])
def confirm_request(request):
    res = json.loads(request.body)['Body']['stkCallback']['ResultCode']
    try:
        if res == 0:
            my_cart = Cart.objects.get(payer_mobile_no=json.loads(request.body)[
                'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'])
            tracking_number = uuid.uuid4().hex.upper()[0:8]
            new_order = Orders(
                tracking_number=tracking_number,
                address=my_cart.address,
                receiver_fname=my_cart.receiver_fname,
                receiver_lname=my_cart.receiver_lname,
                mobile_no=my_cart.mobile_no,
                no_of_regular_batches=my_cart.no_of_regular_batches,
                no_of_premium_batches=my_cart.no_of_premium_batches,
                owner=my_cart.owner
            )
            new_order.save()
            # request.session['order_id'] = new_order.id
            payment = Payments(
                ref_number=json.loads(request.body)[
                    'Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
                amount=json.loads(request.body)[
                    'Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
                mobile_no=json.loads(request.body)[
                    'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'],
                paid_at=json.loads(request.body)[
                    'Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
                order=new_order,
                owner=my_cart.owner
            )
            print(request.session.get('order_id'))
            payment.save()
            my_cart.delete()
            return HttpResponse('Successfully made the payment')
        return HttpResponse('Failure in payment')
    except Exception as e:
        print(e)
        my_cart = Cart.objects.get(payer_mobile_no=json.loads(request.body)[
            'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'])
        my_cart.payer_mobile_no = ''
        my_cart.save()
        return HttpResponse('Failure in payment')


class LipaNaMpesa(graphene.Mutation):
    '''Adds to the cart'''
    # Returns the mpesa success status
    success = graphene.String()

    class Arguments:
        '''Takes in cart details as arguments'''
        mobile_no = graphene.String()
        amount = graphene.Int()

    # @login_required
    def mutate(self, info, **kwargs):
        '''Add to cart mutation'''
        try:
            payer_mobile_no = kwargs.get('payer_mobile_no', None)
            existing_cart = Cart.objects.get(owner=info.context.user)
            existing_cart.payer_mobile_no = payer_mobile_no
            existing_cart.save()
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = os.environ['MPESA_STKPUSH']
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": kwargs.get('amount'),
                "PartyA": kwargs.get('mobile_no'),
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": kwargs.get('mobile_no'),
                "CallBackURL": os.environ['MPESA_CALLBACK_URL'],
                "AccountReference": "Fadhila Network",
                "TransactionDesc": "Fadhila Network"
            }
            response = requests.post(api_url, json=request, headers=headers)
            return LipaNaMpesa(success=json.loads(response.text)['CustomerMessage'])
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occured. The payment could not be completed. Either the request has already been sent on your mobile phone' +
                               ' or there is downtime from our side')


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    lipa_na_mpesa = LipaNaMpesa.Field()
