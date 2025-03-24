# biblia_messages/schema.py
import graphene
import asyncio
from graphene import ObjectType, String
from .services.openrouter import get_biblical_response

class AskBibleCharacter(graphene.ObjectType):
    ask_bible_character = graphene.NonNull(graphene.String,
        message=graphene.String(required=True),
        character=graphene.String(),
        version=graphene.String(default_value='NVI'),
        language=graphene.String(default_value='pt')
    )

    def resolve_ask_bible_character(self, info, message, character=None, version='NVI', language='es'):
        # Ejecuta la función async en el contexto sync de GraphQL
        return asyncio.run(get_biblical_response(
            message=message,
            character=character,
            version=version,
            language=language
        ))
