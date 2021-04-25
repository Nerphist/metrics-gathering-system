from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from auth_service.settings import ADMIN_GROUP_NAME, SERVER_API_KEY


class IsAdminPermission(BasePermission):
    message = 'The user must be in administration group'

    def has_permission(self, request: Request, _=None):
        return is_admin(request.user)


class ServerApiKeyAuthorized(BasePermission):

    def has_permission(self, request, view):
        api_key = request.headers.get('server-api-key')
        if api_key == SERVER_API_KEY:
            return True
        return False


def is_admin(user):
    for group in user.user_groups.all():
        if group.name == ADMIN_GROUP_NAME:
            return True
    return False


def is_super_admin(user):
    for group in user.user_groups.all():
        if group.name == ADMIN_GROUP_NAME and group.admin == user:
            return True
    return False
