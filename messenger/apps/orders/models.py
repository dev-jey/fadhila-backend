'''Model for orders'''
from django.db import models
from messenger.apps.authentication.models import User
from messenger.apps.address.models import Town

# Create your models here.


class Orders(models.Model):
    '''Defines attributes of the card model'''
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'OnMyWay'),
        (2, 'Delivered'),
        )
    tracking_number = models.CharField(max_length=100)
    payment_status = models.IntegerField(null=True)
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True)
    cost_of_cards = models.FloatField()
    transport_fee = models.FloatField()
    total_cost = models.FloatField()
    no_of_cards = models.IntegerField()
    delivery_status = models.IntegerField(null=False,
                                          default=STATUS_CHOICES[0][0],
                                          choices=STATUS_CHOICES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.tracking_number
