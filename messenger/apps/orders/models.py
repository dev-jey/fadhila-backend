'''Model for orders'''
from django.db import models
from messenger.apps.authentication.models import User

# Create your models here.


class Orders(models.Model):
    '''Defines attributes of the order model'''
    tracking_number = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    receiver_fname = models.CharField(max_length=100, null=False, default='')
    receiver_lname = models.CharField(max_length=100, null=False, default='')
    total_no_of_card_batches = models.IntegerField(default=0)
    mobile_no = models.CharField(max_length=12)
    cost_of_cards = models.DecimalField(max_digits=20, decimal_places=2)
    total_cost = models.DecimalField(max_digits=20, decimal_places=2)
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


class Cart(models.Model):
    '''Cart model'''
    no_of_regular_batches = models.IntegerField(default=0)
    no_of_premium_batches = models.IntegerField(default=0)
    receiver_fname = models.CharField(max_length=100, null=False, default='')
    receiver_lname = models.CharField(max_length=100, null=False, default='')
    address = models.CharField(max_length=255, null=False, default='')
    mobile_no = models.CharField(max_length=12, null=False, default='')
    payer_mobile_no = models.CharField(max_length=12, null=True)
    price_of_regular = models.DecimalField(max_digits=20, decimal_places=2)
    price_of_premium = models.DecimalField(max_digits=20, decimal_places=2)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cart if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.owner.username
