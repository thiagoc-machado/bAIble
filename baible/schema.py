import graphene
from progress.schema import MyProgressQuery
from biblia_messages.schema import AskBibleCharacter, Query as BibliaQuery

class Query(MyProgressQuery, AskBibleCharacter, graphene.ObjectType):
    hello = graphene.String(default_value='Hola desde bAIble 👋')

class Query(BibliaQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
