import graphene
from .objects import UserType
from .models import User
from graphene_django.filter import DjangoFilterConnectionField
from .helpers import UserValidations
from graphql import GraphQLError
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from graphql_extensions.auth.decorators import login_required



user_validator = UserValidations()

class Query(graphene.AbstractType):
    profile = graphene.List(UserType, username=graphene.String())
    current_user = graphene.Field(UserType)

    @login_required
    def resolve_profile(self, info, username):
        existing_profile = User.objects.filter(username=username)
        if existing_profile:
            return existing_profile
        raise GraphQLError('User does not exist')
    
    @login_required
    def resolve_current_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Kindly login to continue!')
        return user


class CreateUser(graphene.Mutation):

    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()
    
    def mutate(self, info, **kwargs):
        user_data = user_validator.validate_entered_data(kwargs)
        new_user = User(
            username=user_data['username'], 
            email=user_data['email'], 
            )
        new_user.set_password(make_password(user_data['password']))
        new_user.save()
        return CreateUser(user=new_user)

class UpdateUser(graphene.Mutation):

    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.Int()
        username = graphene.String()
        email = graphene.String()
        is_active = graphene.Boolean()
        bio = graphene.String() 
        image = graphene.String()
    
    @login_required
    def mutate(
        self, info, **kwargs
        ):
        id= kwargs.get('id')
        username = kwargs.get('username')
        email = kwargs.get('email')
        is_active = kwargs.get('is_active')
        bio = kwargs.get('bio')
        image = kwargs.get('image')
        valid_username = user_validator.clean_username(username)
        valid_email = user_validator.clean_email(email)
        if info.context.user.id != id:
            raise GraphQLError("You can only update your own profile")
        user_validator.check_already_existing_during_update(
            info, valid_username, valid_email
            )
        try:
            User.objects.filter(id=id).update(
                username=valid_username,
                email=valid_email,
                bio=bio,
                is_active=is_active,
                image=image
            )
            existing_user = User.objects.get(id=id)
            return UpdateUser(user=existing_user)
        except Exception as e:
            raise GraphQLError(e.messages)
    

class DeactivateAccount(graphene.Mutation):

    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()

    @login_required
    def mutate(self, info, username):
        valid_username = user_validator.clean_username(username)
        user_validator.validate_logged_in(info)
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
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    deactivate_account = DeactivateAccount.Field()



