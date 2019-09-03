from django.db import models

# Create your models here.
class Country(models.Model):
    '''Defines attributes of the home model'''
    #use actual coordinates
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         country if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name