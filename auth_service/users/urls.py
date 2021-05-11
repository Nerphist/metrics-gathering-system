from django.urls import path

from users.views import *

urlpatterns = [
    path('', GetAllUsersView.as_view(), name='Get all users'),
    path('<int:user_id>/', SingleUserView.as_view(), name='Get user'),
    path('change-password/', ChangeUserPasswordView.as_view(), name='Change user password'),
    path('auth-user/', get_user_info, name='Get user by token'),
    path('add-user/', add_user, name='Add user'),

    path('invites/', get_all_created_invitations, name='Get all invited which user has made'),
    path('invites/<str:secret_key>/', GetByInviteView.as_view({'get': 'retrieve'}), name='Get info about invite'),
    path('invites/<str:secret_key>/commit/', ConfirmInviteView.as_view(), name='Accept the invite'),

    path('groups/', UserGroupListView.as_view(), name='Get all groups'),
    path('groups/<int:user_group_id>/', UserGroupRetrieveView.as_view(), name='Get group'),
    path('groups/<int:user_group_id>/add-user/', add_user_to_group, name='Add user to group'),
    path('groups/<int:user_group_id>/add-admin/', add_group_admin, name='Switch group admin'),
    path('groups/<int:user_group_id>/remove-user/<int:user_to_remove_id>', remove_from_group,
         name='Remove user from group'),

    path('contact-info/<int:contact_info_id>/', ContactInfoRetrieveView.as_view(), name='Get contact info'),

]
