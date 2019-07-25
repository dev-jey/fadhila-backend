'''The main schema that houses all the apps in the project'''
import graphene
import graphql_jwt
import messaging.schema
import authentication.schema
from authentication.objects import UserType
from authentication.schema import USER_VALIDATOR

class Query(messaging.schema.Query,
            authentication.schema.Query,
            graphene.ObjectType):
    '''Registers all the queries in each app's schema'''
    pass

class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        email = USER_VALIDATOR.clean_email(kwargs.get('email'))
        USER_VALIDATOR.check_active_and_verified_status(email)
        return cls(user=info.context.user)

class Mutation(authentication.schema.Mutation,
               graphene.ObjectType):
    '''Registers all the mutations in each app's schema'''
    #jwt token auth, verify_token and refresh token mutations
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

SCHEMA = graphene.Schema(query=Query, mutation=Mutation)
