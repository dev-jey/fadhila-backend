'''Model for orders'''
from django.db import models
from messenger.apps.authentication.models import User
from messenger.apps.address.models import Town

# Create your models here.


class Orders(models.Model):
    '''Defines attributes of the order model'''
    tracking_number = models.CharField(max_length=100)
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True)
    cost_of_cards = models.FloatField(default=0)
    transport_fee = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    receiver_fname = models.CharField(max_length=100, null=True)
    receiver_lname = models.CharField(max_length=100, null=True)
    total_no_of_card_batches = models.IntegerField(default=0)
    mobile_no = models.IntegerField(default=0)
    no_of_regular_batches = models.IntegerField(default=0)
    no_of_premium_batches = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         orders if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.tracking_number
