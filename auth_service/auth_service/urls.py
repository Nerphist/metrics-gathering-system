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
from rest_framework_simplejwt.views import token_refresh, token_obtain_pair

from users.views import RegisterView, GetUserView

urlpatterns = [
    path('token/refresh/', token_refresh, name='token_refresh'),
    path('login/', token_obtain_pair, name='login'),
    path('register/', RegisterView.as_view({'post': 'create'}, name='register')),
    path('get-user/<int:user_id>/', GetUserView.as_view({'get': 'retrieve'}, name='get-user')),

]
