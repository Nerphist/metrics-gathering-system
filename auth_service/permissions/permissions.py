from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from auth_service.settings import ADMIN_GROUP_NAME


class IsAdmin(BasePermission):
    message = 'The user must be in administration group'

    def has_permission(self, request: Request, _=None):
        for group in request.user.user_groups:
            if group.name == ADMIN_GROUP_NAME:
                return True
        return False
