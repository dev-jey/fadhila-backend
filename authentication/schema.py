'''User authentication, updating and deactivation'''
#Third party imports
import graphene
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from graphql_extensions.auth.decorators import login_required

#Local imports
from .objects import UserType
from .models import User
from .helpers import UserValidations


USER_VALIDATOR = UserValidations()


class Query(graphene.AbstractType):
    '''Defines queries for the user profile and 
    the currently logged in user'''
    def __init__(self):
        pass
    profile = graphene.List(UserType, username=graphene.String())
    current_user = graphene.Field(UserType)

    @classmethod
    @login_required
    def resolve_profile(cls, info, username):
        '''Resolves the profile of the provided username'''
        existing_profile = User.objects.filter(username=username)
        if existing_profile:
            return existing_profile
        raise GraphQLError('User does not exist')

    @classmethod
    @login_required
    def resolve_current_user(cls, info):
        '''Resolves the currently logged in user'''
        user = info.context.user
        return user


class CreateUser(graphene.Mutation):
    '''Handle creation of a user and saving to the db'''
    #items that the mutation will return
    user = graphene.Field(UserType)
    token = graphene.String()

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
        return CreateUser(user=new_user, token=new_user.token)


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
        is_active = graphene.Boolean()
        bio = graphene.String()
        image = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Gets the new user info and updates it in the db'''
        user_id = kwargs.get('id')
        username = kwargs.get('username')
        email = kwargs.get('email')
        is_active = kwargs.get('is_active')
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
                is_active=is_active,
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
        '''Updates the is_active field and saves the new info'''
        valid_username = USER_VALIDATOR.clean_username(username)
        try:
            existing_user = User.objects.get(username=valid_username)
            if not existing_user.is_active:
                raise GraphQLError('User already deactivated')
            if valid_username != info.context.user.username:
                raise GraphQLError(
                    "You can only update your own profile"
                )
            existing_user.is_active = False
            existing_user.save()
            return DeactivateAccount(user=existing_user)
        except ObjectDoesNotExist:
            raise GraphQLError("The user does not exist")


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    deactivate_account = DeactivateAccount.Field()
