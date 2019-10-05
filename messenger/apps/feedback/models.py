from django.db import models
from messenger.apps.cards.models import Card

# Create your models here.
class Feedback(models.Model):
    '''Defines attributes of the feedback model'''
    #use actual coordinates
    message = models.CharField(max_length=256)
    card =models.ForeignKey(Card, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         country if retrieved'''
        ordering = ('card',)

    def __str__(self):
        return self.card.owner.username