'''The main schema that houses all the apps in the project'''
import graphene
import graphql_jwt
import messaging.schema
import authentication.schema

class Query(messaging.schema.Query,
            authentication.schema.Query,
            graphene.ObjectType):
    '''Registers all the queries in each app's schema'''
    pass

class Mutation(authentication.schema.Mutation,
               graphene.ObjectType):
    '''Registers all the mutations in each app's schema'''
    #Login, verify_token and refresh token mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

SCHEMA = graphene.Schema(query=Query, mutation=Mutation)
