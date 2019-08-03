'''Model for cards'''
from django.db import models
from messenger.apps.authentication.models import User
# Create your models here.


class Card(models.Model):
    '''Defines attributes of the card model'''
    serial = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.serial
