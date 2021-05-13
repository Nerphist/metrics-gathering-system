from rest_framework.permissions import BasePermission

from auth_api import auth_user, has_permission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return auth_user(request.headers)


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return has_permission(request.headers)
