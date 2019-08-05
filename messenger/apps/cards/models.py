'''Model for cards'''
from django.db import models
from messenger.apps.orders.models import Orders
# Create your models here.


class Card(models.Model):
    '''Defines attributes of the card model'''
    serial = models.CharField(max_length=100)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.serial
