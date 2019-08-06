'''Model for addresses'''
from django.db import models
from messenger.apps.authentication.models import User
# Create your models here.


class County(models.Model):
    '''Defines attributes of the card model'''
    name = models.CharField(max_length=100)
    #use actual coordinates
    country = models.CharField(max_length=100, default="Kenya")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name

class Town(models.Model):
    '''Defines attributes of the card model'''
    receiver_fname = models.CharField(max_length=100)
    receiver_lname = models.CharField(max_length=100)
    phone_number = models.IntegerField(null=True)
    #use actual coordinates
    county = models.ForeignKey(County, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100)
    home_address = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.town
