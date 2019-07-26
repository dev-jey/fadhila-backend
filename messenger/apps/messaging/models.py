'''Model for messages'''
from django.db import models

# Create your models here.

class Message(models.Model):
    '''Defines attributes of the messages model'''
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        '''Defines the ordering of the
         messages if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.title
