from django.db import models

# Create your models here.

class Message(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.title