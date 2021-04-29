from rest_framework.authentication import BaseAuthentication

from auth_api import auth_user


class JWTAuthentication(BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        return auth_user(request.headers), True
