'''User authentication, updating and deactivation'''
#Third party imports
import os
import graphene
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from graphql_extensions.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

#Local imports
from messenger.tokens import ACCOUNT_ACTIVATION_TOKEN
from .objects import UserType
from .models import User
from .helpers import UserValidations
from .token_generator import TokenGenerator


USER_VALIDATOR = UserValidations()
TOKEN_GENERATOR = TokenGenerator()


class Query(graphene.AbstractType):
    '''Defines queries for the user profile and 
    the currently logged in user'''
    def __init__(self):
        pass
    profile = graphene.List(UserType, username=graphene.String())
    current_user = graphene.Field(UserType)

    @login_required
    def resolve_profile(self, info, username):
        '''Resolves the profile of the provided username'''
        existing_profile = User.objects.filter(username=username)
        if existing_profile:
            return existing_profile
        raise GraphQLError('User does not exist')

    @login_required
    def resolve_current_user(self, info):
        '''Resolves the currently logged in user'''
        user = info.context.user
        if user.is_anonymous:
            return GraphQLError('Kindly login to continue')
        return user


class CreateUser(graphene.Mutation):
    '''Handle creation of a user and saving to the db'''
    #items that the mutation will return
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
        new_user.save()
        try:
            message = render_to_string('send_activate_email.html', {
                'user':new_user,
                'domain':os.environ['CURRENT_DOMAIN'],
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': ACCOUNT_ACTIVATION_TOKEN.make_token(new_user),
            })
            mail_subject = 'Activate your account at Fadhila.'
            to_email = USER_VALIDATOR.clean_email(kwargs.get('email'))
            stripped_message = strip_tags(message)
            email = EmailMultiAlternatives(mail_subject, stripped_message, to=[to_email])
            email.attach_alternative(message, "text/html")
            email.send()
            return CreateUser(user=new_user)
        except BaseException as error:
            new_user.delete()
            raise GraphQLError('There has been a problem in registering you. '+
                               'Kindly check your internet connection and try again')


class ActivateUser(graphene.Mutation):
    '''Activates a user during registration'''
    #items return from the mutation
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
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
        correct_token = ACCOUNT_ACTIVATION_TOKEN.check_token(user, access_token)
        if not user or not correct_token or user.is_deactivated:
            return GraphQLError('There has been a problem in verifying your account')
        user.is_verified = True
        token = TOKEN_GENERATOR.generate(user.email)
        user.save()
        return ActivateUser(user=user, token=token)

class UpdateUser(graphene.Mutation):
    '''Handles the updating of a user information'''
    #Returns an object of type user
    user = graphene.Field(UserType)

    class Arguments:
        '''Arguments that need to be passed in for an
        update to occur'''
        id = graphene.Int()
        username = graphene.String()
        email = graphene.String()
        is_deactivated = graphene.Boolean()
        bio = graphene.String()
        image = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Gets the new user info and updates it in the db'''
        user_id = kwargs.get('id')
        username = kwargs.get('username')
        email = kwargs.get('email')
        is_deactivated = kwargs.get('is_deactivated')
        bio = kwargs.get('bio')
        image = kwargs.get('image')
        valid_username = USER_VALIDATOR.clean_username(username)
        valid_email = USER_VALIDATOR.clean_email(email)
        if info.context.user.id != user_id:
            raise GraphQLError("You can only update your own profile")
        USER_VALIDATOR.check_already_existing_during_update(
            info, valid_username, valid_email
        )
        try:
            User.objects.filter(id=user_id).update(
                username=valid_username,
                email=valid_email,
                bio=bio,
                is_deactivated=is_deactivated,
                image=image
            )
            existing_user = User.objects.get(id=user_id)
            return UpdateUser(user=existing_user)
        except Exception as error:
            raise GraphQLError(error.messages)


class DeactivateAccount(graphene.Mutation):
    '''Deactivate a user's account'''
    #Returns the deactivated user info
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


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    create_user = CreateUser.Field()
    activate_user = ActivateUser.Field()
    update_user = UpdateUser.Field()
    deactivate_account = DeactivateAccount.Field()
