import graphene
from progress.schema import MyProgressQuery

class Query(MyProgressQuery, graphene.ObjectType):
    hello = graphene.String(default_value='Hola desde bAIble 👋')

schema = graphene.Schema(query=Query)
