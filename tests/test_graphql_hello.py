import pytest
from graphene.test import Client
from baible.schema import schema

@pytest.mark.django_db
def test_hello_query():
    client = Client(schema)
    executed = client.execute('''{ hello }''')
    
    # Espera a string padrão
    assert executed['data']['hello'] == 'Hola desde bAIble 👋'
