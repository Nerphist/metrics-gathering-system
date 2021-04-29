from fastapi import Request, HTTPException

from auth_api import is_admin


def is_admin_permission(request: Request):
    print('1231')
    print('1231')
    print('1231')
    print('1231')
    if not is_admin(request.headers):
        raise HTTPException(detail='User is not admin', status_code=403)
