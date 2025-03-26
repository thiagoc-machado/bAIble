# biblia_messages/schema.py
import graphene
import asyncio
from graphene import ObjectType, String, InputObjectType
from .services.openrouter import get_biblical_response

class AskBibleCharacter(graphene.ObjectType):
    ask_bible_character = graphene.NonNull(graphene.String,
        message=graphene.String(required=True),
        character=graphene.String(),
        version=graphene.String(default_value='NVI'),
        language=graphene.String(default_value='pt'),
        model=graphene.String(),
        history=graphene.List(graphene.String)
    )

class ChatMessageInput(InputObjectType):
    text = graphene.String(required=True)
    isUser = graphene.Boolean(required=True)
    timestamp = graphene.String(required=True)

class Query(ObjectType):
    ask_bible_character = graphene.String(
        message=graphene.String(required=True),
        character=graphene.String(),
        version=graphene.String(default_value='NVI'),
        language=graphene.String(default_value='pt'),
        model=graphene.String(default_value='mistral-7b-instruct'),
        history=graphene.List(ChatMessageInput)
    )

    def resolve_ask_bible_character(self, info, message, character=None, version='NVI', language='pt', model='mistral-7b-instruct', history=None):
        return asyncio.run(get_biblical_response(
            message=message,
            character=character,
            version=version,
            language=language,
            model=model,
            history=history or []
        ))