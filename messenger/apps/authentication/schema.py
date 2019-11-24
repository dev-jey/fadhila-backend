'''User authentication, updating and deactivation'''
# Third party imports
import os
import graphene
import graphql_social_auth
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from graphql_extensions.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from messenger.apps.cards.utils import get_paginator, items_getter_helper

# Local imports
from messenger.tokens import ACCOUNT_ACTIVATION_TOKEN
from messenger.apps.country.models import Country
from .objects import UserType, UserPaginatedType
from .models import User, Subscription
from .helpers import UserValidations
from .token_generator import TokenGenerator


USER_VALIDATOR = UserValidations()
TOKEN_GENERATOR = TokenGenerator()


class Query(graphene.AbstractType):
    '''Defines queries for the user profile and 
    the currently logged in user'''

    def __init__(self):
        pass

    valid_link = graphene.Field(UserType,
                                uidb64=graphene.String(),
                                access_token=graphene.String())
    current_user = graphene.Field(UserType)

    all_users = graphene.Field(UserPaginatedType, page=graphene.Int(),
                               search=graphene.String(), kenyan=graphene.Boolean())

    def resolve_valid_link(self, info, **kwargs):
        '''confirm if the given token and uidb64 are valid,
        and activate the user in the db'''
        uidb64 = kwargs.get('uidb64')
        access_token = kwargs.get('access_token')
        user = validate_uid_and_token(uidb64, access_token)
        return user

    @login_required
    def resolve_current_user(self, info):
        '''Resolves the currently logged in user'''
        user = info.context.user
        if user.is_anonymous:
            return GraphQLError('Kindly login to continue')
        return user
    
    @login_required
    def resolve_all_users(self, info, **kwargs):
        page = kwargs.get('page')
        search = kwargs.get('search')
        kenyan = kwargs.get('kenyan')
        _filter = (
            Q(email__icontains='')
        )
        users = User.objects.all().order_by('email')
        try:
            if search:
                _filter = (
                    Q(email__icontains=search)
                )
                users = User.objects.filter(_filter).order_by('email')
            if kenyan:
                users = User.objects.filter(country__code='KE').filter(_filter).order_by('email')
            return items_getter_helper(page, users, UserPaginatedType)
        except Exception as e:
            print(e)
            raise GraphQLError('An error occured while getting users')


class CreateUser(graphene.Mutation):
    '''Handle creation of a user and saving to the db'''
    # items that the mutation will return
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments to be passed in during the user creation'''
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()

    def mutate(self, info, **kwargs):
        '''Mutation for user creation. Actual saving happens here'''
        user_data = USER_VALIDATOR.validate_entered_data(kwargs)
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
        )
        new_user.set_password(user_data['password'])
        new_user.is_verified = False
        new_user.save()
        try:
            message = render_to_string('send_activate_email.html', {
                'user': new_user,
                'domain': os.environ['CURRENT_DOMAIN'],
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': ACCOUNT_ACTIVATION_TOKEN.make_token(new_user),
            })
            mail_subject = 'Activate your account at Fadhila.'
            to_email = USER_VALIDATOR.clean_email(kwargs.get('email'))
            send_mail(message, mail_subject, to_email)
            return CreateUser(user=new_user)
        except BaseException as e:
            print(e)
            new_user.delete()


class ActivateUser(graphene.Mutation):
    '''Activates a user during registration'''
    # items return from the mutation
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        uidb64 = graphene.String()
        access_token = graphene.String()

    def mutate(self, info, **kwargs):
        '''confirm if the given token and uidb64 are valid,
        and activate the user in the db'''
        uidb64 = kwargs.get('uidb64')
        access_token = kwargs.get('access_token')
        try:
            user = validate_uid_and_token(uidb64, access_token)
            user.is_verified = True
            token = TOKEN_GENERATOR.generate(user.email)
            user.save()
            return ActivateUser(user=user, token=token)
        except BaseException as e:
            print(e)
            raise GraphQLError("An error occured in activating account")


class ResetPassword(graphene.Mutation):
    '''Sends a user password reset link'''
    # items return from the mutation
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        email = graphene.String()

    def mutate(self, info, email, **kwargs):
        '''Receive the user email and send the reset link'''

        new_email = USER_VALIDATOR.clean_email(email)
        USER_VALIDATOR.check_email_validity(new_email)
        try:
            user = User.objects.get(email=new_email)
        except BaseException:
            return GraphQLError('A user with the given email was not found')

        message = render_to_string('send_password_reset.html', {
            'user': user,
            'domain': os.environ['CURRENT_DOMAIN'],
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': ACCOUNT_ACTIVATION_TOKEN.make_token(user),
        })
        mail_subject = 'Hi there, here is your password reset link.'
        send_mail(message, mail_subject, new_email)
        return ResetPassword(user=user)


class ContactUs(graphene.Mutation):
    '''Creates a contact email to admins'''
    # items return from the mutation
    user = graphene.String()

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        name = graphene.String()
        email = graphene.String()
        mobile_no = graphene.String()
        message = graphene.String()

    def mutate(self, info, **kwargs):
        '''Receive the user details then sends email to admin'''

        new_email = USER_VALIDATOR.clean_email(kwargs.get('email'))
        USER_VALIDATOR.check_email_validity(new_email)
        message = render_to_string('send_contact.html', {
            'email': new_email,
            'name': kwargs.get('name'),
            'mobile_no': kwargs.get('mobile_no'),
            'message': kwargs.get('message')
        })
        mail_subject = 'Help Request from '+kwargs.get('name')
        send_mail(message, mail_subject,
                  os.environ['FADHILA_HELP_DESK'], new_email)
        return ContactUs(user=kwargs.get('name'))


class Subscribe(graphene.Mutation):
    '''Users subscribe to newsletters'''
    # items return from the mutation
    success = graphene.String()

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        email = graphene.String()

    def mutate(self, info, **kwargs):
        '''Receive the user email and saves the data'''
        new_email = USER_VALIDATOR.clean_email(kwargs.get('email'))
        USER_VALIDATOR.check_email_validity(new_email)
        try:
            user = Subscription.objects.get(email=new_email)
            if user:
                return GraphQLError('You are already subscribed to our newsletters')
        except BaseException:
            new_subscriber = Subscription(
                email=new_email
            )
            new_subscriber.save()
            return Subscribe(success="You are successfully subscribed")


class UpdatePassword(graphene.Mutation):
    '''Activates a user during registration'''
    # items return from the mutation
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        uidb64 = graphene.String()
        access_token = graphene.String()
        password = graphene.String()
        confirm_password = graphene.String()

    def mutate(self, info, **kwargs):
        '''confirm if the given token and uidb64 are valid,
        and activate the user in the db'''
        uidb64 = kwargs.get('uidb64')
        access_token = kwargs.get('access_token')
        user = validate_uid_and_token(uidb64, access_token)
        password = USER_VALIDATOR.clean_password(kwargs.get('password'))
        confirm_password = USER_VALIDATOR.clean_password(
            kwargs.get('confirm_password'))
        USER_VALIDATOR.validate_password(password)
        if password != confirm_password:
            return GraphQLError('The given passwords do not match')
        user.set_password(password)
        user.save()
        return UpdatePassword(user=user)



class ChangePassword(graphene.Mutation):
    '''Activates a user during registration'''
    # items return from the mutation
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments that will be passed to the mutation'''
        current_password = graphene.String()
        password = graphene.String()
        confirm_password = graphene.String()

    def mutate(self, info, **kwargs):
        '''change password in the db'''
        current_password = USER_VALIDATOR.clean_password(kwargs.get('current_password'))
        password = USER_VALIDATOR.clean_password(kwargs.get('password'))
        confirm_password = USER_VALIDATOR.clean_password(
            kwargs.get('confirm_password'))
        pass_match = info.context.user.check_password(current_password)
        if not pass_match:
            return GraphQLError('The current password is wrong')
        USER_VALIDATOR.validate_password(current_password)
        if password != confirm_password:
            return GraphQLError('The new passwords do not match')
        info.context.user.set_password(password)
        info.context.user.save()
        return ChangePassword(user=info.context.user)



class UpdateProfile(graphene.Mutation):
    '''Handles the updating of a user information'''
    # Returns an object of type user
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments that need to be passed in for an
        update to occur'''
        username = graphene.String()
        email = graphene.String()
        bio = graphene.String()
        image = graphene.String()
        country = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Gets the new user info and updates it in the db'''
        username = kwargs.get('username')
        email = kwargs.get('email')
        bio = kwargs.get('bio')
        image = kwargs.get('image')
        country = kwargs.get('country')
        valid_username = USER_VALIDATOR.clean_username(username)
        valid_email = USER_VALIDATOR.clean_email(email)
        USER_VALIDATOR.check_already_existing_during_update(
            info, valid_username
        )
        try:
            user = User.objects.get(email=valid_email)
            user.username = valid_username
            user.bio = bio
            user.image = image
            country_id = Country.objects.get(code=country)
            user.country = country_id
            user.save()
            return UpdateProfile(user=user)
        except Exception as e:
            print(e)
            raise GraphQLError('There has been an error updating your profile.'
                               + ' Try again later')


class DeactivateAccount(graphene.Mutation):
    '''Deactivate a user's account'''
    # Returns the deactivated user info
    user = graphene.Field(UserType)

    class Arguments:
        '''Takes in a username as an argument'''
        username = graphene.String()

    @login_required
    def mutate(self, info, username):
        '''Updates the is_deactivated field and saves the new info'''
        valid_username = USER_VALIDATOR.clean_username(username)
        try:
            existing_user = User.objects.get(username=valid_username)
            if not existing_user.is_deactivated:
                raise GraphQLError('User already deactivated')
            if valid_username != info.context.user.username:
                raise GraphQLError(
                    "You can only update your own profile"
                )
            existing_user.is_deactivated = False
            existing_user.save()
            return DeactivateAccount(user=existing_user)
        except ObjectDoesNotExist:
            raise GraphQLError("The user does not exist")


class SocialAuth(graphql_social_auth.SocialAuthMutation):

    user = graphene.Field(UserType)
    token = graphene.String()

    @classmethod
    def resolve(cls, root, info, social, **kwargs):
        token = TOKEN_GENERATOR.generate(social.user.email)
        return cls(user=social.user, token=token)


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    create_user = CreateUser.Field()
    activate_user = ActivateUser.Field()
    reset_password = ResetPassword.Field()
    social_auth = SocialAuth.Field()
    update_password = UpdatePassword.Field()
    update_profile = UpdateProfile.Field()
    contact_us = ContactUs.Field()
    subscribe_me = Subscribe.Field()
    change_password = ChangePassword.Field()
    deactivate_account = DeactivateAccount.Field()


def send_mail(message, mail_subject, to_email, from_email=None):
    try:
        stripped_message = strip_tags(message)
        email = EmailMultiAlternatives(
            mail_subject, stripped_message, from_email, to=[to_email])
        email.attach_alternative(message, "text/html")
        email.send()
    except BaseException as error:
        print(error)
        raise GraphQLError('There has been a problem in sending a link. ' +
                           'Kindly check your internet connection and try again')


def validate_uid_and_token(uidb64, access_token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    correct_token = ACCOUNT_ACTIVATION_TOKEN.check_token(user, access_token)
    if not user or not correct_token:
        raise GraphQLError('There given link is either expired or incorrect')
    if user.is_deactivated:
        raise GraphQLError('The user is currently deativated')
    return user
