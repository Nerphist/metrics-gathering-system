from rest_framework.permissions import BasePermission

from auth_service.settings import ADMIN_GROUP_NAME, SERVER_API_KEY


class ServerApiKeyAuthorized(BasePermission):

    def has_permission(self, request, view):
        api_key = request.headers.get('Server-Api-Key')
        if api_key == SERVER_API_KEY:
            return True
        return False


def is_super_admin(user):
    for group in user.administrated_groups.all():
        if group.name == ADMIN_GROUP_NAME:
            return True
    return False
