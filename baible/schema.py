import graphene
from progress.schema import MyProgressQuery
from biblia_messages.schema import AskBibleCharacter

class Query(MyProgressQuery, AskBibleCharacter, graphene.ObjectType):
    hello = graphene.String(default_value='Hola desde bAIble 👋')

schema = graphene.Schema(query=Query)
