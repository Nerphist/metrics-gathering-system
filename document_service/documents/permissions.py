from rest_framework.permissions import BasePermission

from auth_api import auth_user, is_admin


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return auth_user(request.headers)


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return is_admin(request.headers)
