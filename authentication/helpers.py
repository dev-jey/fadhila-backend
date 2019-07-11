from graphql import GraphQLError
from .models import User
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth.password_validation import validate_password

class UserValidations(object):
    
    def validate_entered_data(self, kwargs):
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
    
    def clean_username(self, username):
        received_username = username.strip()
        return received_username[0].upper() + received_username[1:].lower()
    
    def clean_email(self, email):
        return email.strip().lower()
    
    def clean_password(self, password):
        return password.strip()


    def check_already_existing(self, username, email):
        username_existing = User.objects.filter(username=username)
        if username_existing:
            raise GraphQLError('Username already exists')
        email_existing = User.objects.filter(email=email)
        if email_existing:
            raise GraphQLError('Email already exists')
    
    def check_already_existing_during_update(self, info, username, email):
        try:
            username_existing = User.objects.get(username=username)
            if username_existing and info.context.user != username_existing:
                raise GraphQLError('Username already taken')
            email_existing = User.objects.get(email=email)
            if email_existing and info.context.user.email != email_existing.email:
                raise GraphQLError('Email already taken')
        except Exception:
            return True

    def check_email_validity(self, email):
        try:
           validate_email(email)
        except ValidationError:
            raise GraphQLError('Enter a valid email')


    def check_empty_fields(self, username, email, password):
        if not username:
            raise GraphQLError('Enter a username')
        if not email:
            raise GraphQLError('Enter an email')
        if not password:
            raise GraphQLError('Enter a password')
    
    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise GraphQLError(e.messages[0])