import pesapal
import os
import uuid
from urllib.request import urlopen
import requests
import datetime
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse
import json
from graphql_extensions.auth.decorators import login_required
from graphql import GraphQLError
import graphene
from graphene import ObjectType, String
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential
from django.views.decorators.http import require_http_methods
from messenger.apps.orders.models import Orders, Cart
from .models import Payments, PaymentsTracker
from .objects import PaymentType
from messenger.apps.orders.objects import OrderType

pesapal.consumer_key = os.environ['PESAPAL_KEY']
pesapal.consumer_secret = os.environ['PESAPAL_SECRET']
pesapal.testing =  False


class Query(graphene.AbstractType):

    def __init__(self):
        pass

    save_tracking_details = graphene.Field(OrderType, pesapal_merchant_reference=graphene.String(
    ), pesapal_transaction_tracking_id=graphene.String())

    check_payment_details = graphene.Field(OrderType, tracking_number=graphene.String())

    def resolve_save_tracking_details(self, info, **kwargs):
        try:
            my_cart = Cart.objects.get(owner=info.context.user.id)
            tracking_number = uuid.uuid4().hex.upper()[0:8]
            new_order = Orders(
                tracking_number=tracking_number,
                status="P",
                address=my_cart.address,
                receiver_fname=my_cart.receiver_fname,
                receiver_lname=my_cart.receiver_lname,
                mobile_no=my_cart.mobile_no,
                no_of_regular_batches=my_cart.no_of_regular_batches,
                no_of_premium_batches=my_cart.no_of_premium_batches,
                total_cost=my_cart.total_price,
                owner=my_cart.owner
            )
            new_order.save()
            my_cart.delete()

            track = PaymentsTracker(
                order=new_order,
                tracking_number = tracking_number,
                pesapal_merchant_reference=kwargs.get(
                    'pesapal_merchant_reference'),
                pesapal_transaction_tracking_id=kwargs.get(
                    'pesapal_transaction_tracking_id')
            )
            track.save()
            return new_order
        except Exception:
            pass

    def resolve_check_payment_details(self, info, **kwargs):
        tracking_number = kwargs.get('tracking_number')
        try:
            track_details = PaymentsTracker.objects.get(tracking_number=tracking_number)
            post_params = {
                'pesapal_merchant_reference': track_details.pesapal_merchant_reference,
                'pesapal_transaction_tracking_id': track_details.pesapal_transaction_tracking_id
            }
            new_order = Orders.objects.get(tracking_number=tracking_number)
            url = pesapal.queryPaymentDetails(post_params)
            response = urlopen(url)
            res = str(response.read().decode('utf-8'))[22:]
            if(res.split(',')[2] == 'INVALID'):
                new_order.status = 'C'
                new_order.save()
            if(res.split(',')[2] == 'FAILED'):
                new_order.status = 'C'
                new_order.save()
            payment_mode = 'U'
            if(res.split(',')[1] == 'MPESA'):
                payment_mode = 'M'
            if(res.split(',')[1] == 'ZAP'):
                payment_mode = 'A'
            if(res.split(',')[1] == 'COOPMOBILE'):
                payment_mode = 'C'
            if(res.split(',')[1] == 'KREPMOBILE'):
                payment_mode = 'K'
            if(res.split(',')[2] == 'COMPLETED'):
                new_order.status = 'S'
                new_order.save()
                payment = Payments(
                    ref_number=res.split(',')[0],
                    amount=new_order.total_cost,
                    mobile_no='N/A',
                    payment_mode=payment_mode,
                    paid_at=datetime.datetime.now(),
                    order=new_order,
                    owner=new_order.owner
                )
                payment.save()
            return new_order
        except BaseException as e:
            print(e)


class PesapalPayment(graphene.Mutation):
    '''Handles payments'''
    # Returns the mpesa success status
    url = graphene.String()

    class Arguments:
        '''Takes in mobile_no and amount details as arguments'''
        mobile_no = graphene.String()
        amount = graphene.Int()

    # @login_required
    def mutate(self, info, **kwargs):
        '''Lipa na mpesa mutation'''
        mobile_no = kwargs.get("mobile_no")
        amount = kwargs.get("amount")
        try:
            post_params = {
                'oauth_callback': 'http://localhost:3000/pesapal/confirm/'
            }
            tracking_number = uuid.uuid4().hex.upper()[0:8]
            request_data = {
                'Amount': str(1),
                'Currency': 'KES',
                'Description': 'Cards purchase',
                'Type': 'MERCHANT',
                'Reference': tracking_number,
                'PhoneNumber': mobile_no
            }
            # build url to redirect user to confirm payment
            url = pesapal.postDirectOrder(post_params, request_data)
            return PesapalPayment(url=url)
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occured. Please try again')


# @require_http_methods(["POST"])
# def confirm_request(request, order_id):
#     res = json.loads(request.body)['Body']['stkCallback']['ResultCode']
#     new_order = Orders.objects.get(id=order_id)
#     new_order.created_at = datetime.datetime.now()
#     new_order.updated_at = datetime.datetime.now()
#     if res != 0:
#         new_order.status = 'C'
#         new_order.save()
#     else:
#         new_order.status = 'S'
#         new_order.save()
#     try:
#         my_cart = Cart.objects.get(payer_mobile_no=json.loads(request.body)[
#             'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'])
#         payment = Payments(
#             ref_number=json.loads(request.body)[
#                 'Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
#             amount=json.loads(request.body)[
#                 'Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
#             mobile_no=json.loads(request.body)[
#                 'Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'],
#             payment_mode='M',
#             paid_at=json.loads(request.body)[
#                 'Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
#             order=new_order,
#             owner=new_order.owner
#         )
#         payment.save()
#         my_cart.delete()
#         return HttpResponse('Successfully made the payment')
#     except Exception as e:
#         print(e)
#         return HttpResponse('Failure in payment')


# class LipaNaMpesa(graphene.Mutation):
#     '''Handles payments'''
#     # Returns the mpesa success status
#     success = graphene.String()

#     class Arguments:
#         '''Takes in mobile_no and amount details as arguments'''
#         mobile_no = graphene.String()
#         amount = graphene.Int()

#     @login_required
#     def mutate(self, info, **kwargs):
#         '''Lipa na mpesa mutation'''
#         try:
#             payer_mobile_no = kwargs.get('mobile_no')
#             my_cart = Cart.objects.get(owner=info.context.user)
#             my_cart.payer_mobile_no = payer_mobile_no
#             my_cart.save()
#             access_token = MpesaAccessToken.validated_mpesa_access_token
#             api_url = os.environ['MPESA_STKPUSH']
#             headers = {"Authorization": "Bearer %s" % access_token}
#             tracking_number = uuid.uuid4().hex.upper()[0:8]
#             new_order = Orders(
#                 tracking_number=tracking_number,
#                 address=my_cart.address,
#                 receiver_fname=my_cart.receiver_fname,
#                 receiver_lname=my_cart.receiver_lname,
#                 mobile_no=my_cart.mobile_no,
#                 no_of_regular_batches=my_cart.no_of_regular_batches,
#                 no_of_premium_batches=my_cart.no_of_premium_batches,
#                 total_cost=my_cart.total_price,
#                 owner=my_cart.owner
#             )
#             new_order.save()
#             request = {
#                 "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#                 "Password": LipanaMpesaPpassword.decode_password,
#                 "Timestamp": LipanaMpesaPpassword.lipa_time,
#                 "TransactionType": "CustomerPayBillOnline",
#                 "Amount": kwargs.get('amount'),
#                 "PartyA": kwargs.get('mobile_no'),
#                 "PartyB": LipanaMpesaPpassword.Business_short_code,
#                 "PhoneNumber": kwargs.get('mobile_no'),
#                 "CallBackURL": f"{os.environ['MPESA_CALLBACK_URL']}/{new_order.id}/",
#                 "AccountReference": "Fadhila Network",
#                 "TransactionDesc": "Fadhila Network"
#             }
#             response = requests.post(api_url, json=request, headers=headers)
#             return LipaNaMpesa(success=json.loads(response.text)['CustomerMessage'])
#         except BaseException as e:
#             print(e)
#             raise GraphQLError('An error occured. Please try again')


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
                status="S",
                no_of_regular_batches=my_cart.no_of_regular_batches,
                no_of_premium_batches=my_cart.no_of_premium_batches,
                total_cost=my_cart.total_price,
                owner=my_cart.owner
            )
            if my_cart.owner.country.code == "KE":
                new_order.receiver_fname = my_cart.receiver_fname,
                new_order.receiver_lname = my_cart.receiver_lname,
                new_order.mobile_no = my_cart.mobile_no
                new_order.address = my_cart.address
            else:
                new_order.receiver_fname = '',
                new_order.receiver_lname = '',
                new_order.mobile_no = ''

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
    # lipa_na_mpesa = LipaNaMpesa.Field()
    pesapal_payment = PesapalPayment.Field()
    paypal_payment = PaypalPayment.Field()
