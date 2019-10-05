from django.db import models

# Create your models here.
class Locations(models.Model):
    '''Defines attributes of the locations model'''
    #use actual coordinates
    name = models.CharField(max_length=100)
    transport_fee = models.DecimalField(max_digits=20, decimal_places=2)
    tax = models.DecimalField(max_digits=20, decimal_places=2)
    total_transport_fee = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         country if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name