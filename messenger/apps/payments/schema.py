from django.http import HttpResponse
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from graphql_extensions.auth.decorators import login_required
from graphql import GraphQLError
import graphene
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential


class LipaNaMpesa(graphene.Mutation):
    '''Adds to the cart'''
    # Returns the mpesa success status 
    success = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Add to cart mutation'''
        try:
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = os.environ['MPESA_STKPUSH']
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": 1,
                "PartyA": 254708197333,
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": 254708197333,
                "CallBackURL": os.environ['MPESA_CALLBACK_URL'],
                "AccountReference": "James",
                "TransactionDesc": "Testing stk push"
            }
            response = requests.post(api_url, json=request, headers=headers)
            return LipaNaMpesa(success='success')
        except BaseException as e:
            print(e)
            raise GraphQLError('An error occured. The payment could not be completed')

class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    lipa_na_mpesa = LipaNaMpesa.Field()