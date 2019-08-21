'''User model module'''
from datetime import datetime, timedelta
import jwt
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from messenger import settings

class UserManager(BaseUserManager):
    '''Overrides some methods in the base user manager
    to enable tweaking of some aspects'''
    def create_user(self, username, email, password=None):
        '''A helper method in the creation of a super user'''
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password):
        '''Creates a super user'''
        if password is None:
            raise TypeError('Superusers must have a password.')
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Defines the attributes in the user model'''
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_deactivated = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    image = models.TextField(
        "image",
        default="https://res.cloudinary.com/dw675k0f5/image/upload/v1564061781/storo/Screen_Shot_2019-07-25_at_16.35.29.png")
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return self.username
