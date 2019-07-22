'''Validation helpers for the User model'''
#Third party imports
from graphql import GraphQLError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
#Local imports
from .models import User


class UserValidations(object):
    '''Validations for the user email, username and password'''
    def validate_entered_data(self, kwargs):
        '''Runs all the validations in one function'''
        input_username = kwargs.get('username')
        input_email = kwargs.get('email')
        input_password = kwargs.get('password')
        self.check_empty_fields(input_username, input_email, input_password)
        email = self.clean_email(input_email)
        username = self.clean_username(input_username)
        password = self.clean_password(input_password)
        self.check_email_validity(email)
        self.validate_password(password)
        self.check_already_existing(username, email)
        return {
            'username': username,
            'email': email,
            'password': password
        }
    @classmethod
    def clean_username(cls, username):
        '''Cleans the username'''
        received_username = username.strip()
        return received_username[0].upper() + received_username[1:].lower()

    @classmethod
    def clean_email(cls, email):
        '''Cleans the email'''
        return email.strip().lower()

    @classmethod
    def clean_password(cls, password):
        '''Cleans the password'''
        return password.strip()

    @classmethod
    def check_already_existing(cls, username, email):
        '''Checks if the email or username is already existing'''
        username_existing = User.objects.filter(username=username)
        if username_existing:
            raise GraphQLError('Username already exists')
        email_existing = User.objects.filter(email=email)
        if email_existing:
            raise GraphQLError('Email already exists')


    def check_already_existing_during_update(self, info, username, email):
        '''Checks if the details are already taken by another user
        before updating the current user info'''
        try:
            username_existing = User.objects.get(username=username)
            if username_existing and info.context.user != username_existing:
                raise GraphQLError('Username already taken')
            email_existing = User.objects.get(email=email)
            if email_existing and info.context.user.email != email_existing.email:
                raise GraphQLError('Email already taken')
        except ValidationError:
            return True

    @classmethod
    def check_email_validity(cls, email):
        '''Check if the given mail is valid'''
        try:
            validate_email(email)
        except ValidationError:
            raise GraphQLError('Enter a valid email')

    @classmethod
    def check_empty_fields(cls, username, email, password):
        '''Checks if empty fields are submitted'''
        if not username:
            raise GraphQLError('Enter a username')
        if not email:
            raise GraphQLError('Enter an email')
        if not password:
            raise GraphQLError('Enter a password')

    @classmethod
    def validate_password(cls, password):
        '''Validates a given password'''
        try:
            validate_password(password)
        except ValidationError as error:
            raise GraphQLError(error.messages[0])
