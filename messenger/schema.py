import graphene

import messaging.schema
import authentication.schema


class Query(
    messaging.schema.Query,
    authentication.schema.Query,
    graphene.ObjectType):
    pass

class Mutation(
    authentication.schema.Mutation,
    graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)