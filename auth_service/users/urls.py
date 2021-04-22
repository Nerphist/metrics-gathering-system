from django.urls import path

from users.views import *

urlpatterns = [
    path('', GetAllUsersView.as_view({'get': 'list'}, name='Get all users')),
    path('<int:user_id>/', GetUserView.as_view({'get': 'retrieve'}, name='Get user')),
    path('auth-user/', get_user_info, name='Get user by token'),
    path('add-user/', add_user, name='Add user'),

    path('invites/', get_all_created_invitations, name='Get all invited which user has made'),
    path('invites/<str:secret_key>/', GetByInviteView.as_view({'get': 'retrieve'}), name='Get info about invite'),
    path('invites/<str:secret_key>/commit/', ConfirmInviteView.as_view(), name='Accept the invite'),

    path('groups/', UserGroupListView.as_view(), name='Get all groups'),
    path('groups/<int:user_group_id>/', UserGroupRetrieveView.as_view(), name='Get group'),
    path('groups/<int:user_group_id>/add-user/', add_user_to_group, name='Add user to group'),
    path('groups/<int:user_group_id>/switch-admin/', switch_user_group_admin, name='Switch group admin'),

]
