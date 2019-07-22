'''Admin module for the messaging app'''
from django.contrib import admin
from .models import Message
# Register your models here.

admin.site.register(Message)
