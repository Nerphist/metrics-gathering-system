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
from django.urls import path
from rest_framework_simplejwt.views import token_refresh

from users.views import RegisterView, GetUserView, LoginView, get_user_info

urlpatterns = [
    path('token/refresh/', token_refresh, name='Token refresh'),
    path('login/', LoginView.as_view(), name='Login'),
    path('register/', RegisterView.as_view({'post': 'create'}, name='Register')),
    path('get-user/<int:user_id>/', GetUserView.as_view({'get': 'retrieve'}, name='Get user')),
    path('auth_user/', get_user_info, name='Get user by token'),
]
