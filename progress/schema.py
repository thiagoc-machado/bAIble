import graphene
from graphene_django.types import DjangoObjectType
from .models import Progress

class ProgressType(DjangoObjectType):
    class Meta:
        model = Progress

class MyProgressQuery(graphene.ObjectType):
    my_progress = graphene.List(ProgressType)

    def resolve_my_progress(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Autenticación requerida')

        return Progress.objects.filter(user=user).order_by('-date')
