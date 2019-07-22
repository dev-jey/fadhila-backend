'''The main schema that houses all the apps in the project'''
import graphene
import graphql_jwt
import messaging.schema
import authentication.schema
from authentication.objects import UserType


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    '''Overrides this class to return a user's info after login'''
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, info):
        '''Returns a user object with the logged in user's info'''
        return cls(user=info.context.user)

class Query(messaging.schema.Query,
            authentication.schema.Query,
            graphene.ObjectType):
    '''Registers all the queries in each app's schema'''
    pass

class Mutation(authentication.schema.Mutation,
               graphene.ObjectType):
    '''Registers all the mutations in each app's schema'''
    #Login, verify_token and refresh token mutations
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

SCHEMA = graphene.Schema(query=Query, mutation=Mutation)
