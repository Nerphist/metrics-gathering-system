"""auth_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import token_refresh

from auth_service.settings import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_GROUP_NAME
from users.models import UserGroup, User
from users.urls import urlpatterns as user_urls
from permissions.urls import urlpatterns as permission_urls
from users.views import LoginView, LogoutView


def create_admin():
    try:
        admin = User.objects.create(email=ADMIN_EMAIL, password=make_password(ADMIN_PASSWORD), first_name='admin',
                                    last_name='admin')
        admin_group = UserGroup.objects.create(name=ADMIN_GROUP_NAME, admin=admin)
        admin_group.users.add(admin)
    except:
        pass


create_admin()

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('token/refresh/', token_refresh, name='Token refresh'),
    path('login/', LoginView.as_view(), name='Login'),
    path('logout/', LogoutView.as_view(), name='Logout'),
    url(r'^users/', include(user_urls)),
    url(r'^permissions/', include(permission_urls)),
]
