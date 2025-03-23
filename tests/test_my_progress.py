import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from graphene.test import Client as GQLClient
from baible.schema import schema
from progress.models import Progress

User = get_user_model()

@pytest.mark.django_db
def test_my_progress_authenticated():
    user = User.objects.create_user(username='usuario', password='senha123')
    Progress.objects.create(user=user, goal_completed=True)
    Progress.objects.create(user=user, goal_completed=False)

    factory = RequestFactory()
    request = factory.post('/graphql/')
    request.user = user

    client = GQLClient(schema)
    executed = client.execute(
        '''
        query {
            myProgress {
                date
                goalCompleted
            }
        }
        ''',
        context_value=request
    )

    data = executed['data']['myProgress']
    assert len(data) == 2

@pytest.mark.django_db
def test_my_progress_unauthenticated():
    factory = RequestFactory()
    request = factory.post('/graphql/')
    request.user = AnonymousUser()

    client = GQLClient(schema)
    executed = client.execute(
        '''
        query {
            myProgress {
                date
                goalCompleted
            }
        }
        ''',
        context_value=request
    )

    assert 'errors' in executed
    assert executed['errors'][0]['message'] == 'Autenticación requerida'
