import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(default_value='Hola desde bAIble 👋')

schema = graphene.Schema(query=Query)