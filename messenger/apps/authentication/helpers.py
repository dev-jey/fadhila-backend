'''Validation helpers for the User model'''
#Third party imports
from graphql import GraphQLError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
#Local imports
from .models import User


class UserValidations(object):
    '''Validations for the user email, username and password'''
    def validate_entered_data(self, kwargs):
        '''Runs all the validations in one function'''
        input_username = kwargs.get('username', None)
        input_email = kwargs.get('email', None)
        input_password = kwargs.get('password', None)
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


    def check_already_existing(self, username, email):
        '''Checks if the email or username is already existing'''
        try:
            username_existing = User.objects.get(username=username)
        except ObjectDoesNotExist:
            username_existing = None

        if username_existing:
            raise GraphQLError('Username already exists')

        self.check_mail_already_existing(email)

    @classmethod
    def check_mail_already_existing(cls, email):
        '''Checks if email already exists in the db'''
        try:
            email_existing = User.objects.get(email=email)
        except ObjectDoesNotExist:
            email_existing = None

        if email_existing and email_existing.is_verified:
            raise GraphQLError('Email already exists')
        if email_existing and not email_existing.is_verified:
            raise GraphQLError('Account already created.'+
                               'Kindly verify it via email to continue')

    @classmethod
    def check_active_and_verified_status(cls, email):
        '''checks whether the account is deactivated or unverified'''
        try:
            email_existing = User.objects.get(email=email)
        except ObjectDoesNotExist:
            email_existing = None

        if email_existing and email_existing.is_deactivated:
            raise GraphQLError('Account is temporarily deactivated.' +
                               'Kindly activate it to continue.')
        if email_existing and not email_existing.is_verified:
            raise GraphQLError('Account is not verified.'+
                               'Kindly verify your account via the link sent to your '+
                               'email to continue')



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
