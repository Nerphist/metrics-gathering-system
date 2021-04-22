from django.urls import path

from permissions.views import *

urlpatterns = [
    path('', get_permissions, name='Get all user permissions for action type'),

]
