import os

from fastapi import Request, HTTPException
from starlette import status

from auth_api import get_user, SERVER_API_KEY


def has_permission(request: Request, permission_name):
    if os.environ.get('DEBUG') == 'True':
        return True
    if dict(request.headers).get('Server-Api-Key') == SERVER_API_KEY:
        return
    user = get_user(request)
    if permission_name not in user.permissions:
        raise HTTPException(detail='User has no permissions for this action', status_code=status.HTTP_403_FORBIDDEN)
    return
