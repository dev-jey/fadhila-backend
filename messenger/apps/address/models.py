'''Model for addresses'''
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class HomeAddress(models.Model):
    '''Defines attributes of the home model'''
    #use actual coordinates
    town = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         cards if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name
