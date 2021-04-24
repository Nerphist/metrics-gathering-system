from django.urls import path

from permissions.views import *

urlpatterns = [
    path('', PermissionsListView.as_view(), name='Get all user permissions'),
]
