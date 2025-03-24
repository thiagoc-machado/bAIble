import pytest
from graphene.test import Client
from baible.schema import schema
from unittest.mock import AsyncMock, patch

client = Client(schema)

@pytest.mark.django_db
@patch('biblia_messages.schema.get_biblical_response', new_callable=AsyncMock)
def test_ask_bible_character(mock_response):
    mock_response.return_value = 'No temas, porque yo estoy contigo. —Isaías 41:10'

    executed = client.execute('''
        query {
            askBibleCharacter(
                message: "¿Qué hago cuando tengo miedo?",
                character: "Isaías",
                version: "NVI",
                language: "es"
            )
        }
    ''')

    print(executed)
    data = executed['data']['askBibleCharacter']
    assert 'No temas' in data
