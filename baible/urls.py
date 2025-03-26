
from django.contrib import admin
from django.urls import path, re_path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.urls import include
from django.views.generic import TemplateView


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('auth/accounts/', include('allauth.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
