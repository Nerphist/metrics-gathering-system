import os
from typing import Dict, List

import requests
from pydantic import BaseModel

from document_service.settings import AUTH_SERVICE_HOST, AUTH_SERVICE_PORT

AUTH_API_URL = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"

SERVER_API_KEY = os.environ.get('SERVER_API_KEY', '123')


class UserModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    permissions: List[str]


def auth_user(headers: Dict[str, str]) -> bool:
    if os.environ.get('DEBUG') == 'True':
        return True
    response = requests.get(url=f'{AUTH_API_URL}/users/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    return response.status_code == 200


def get_request_user(headers: Dict[str, str]) -> UserModel:
    response = requests.get(url=f'{AUTH_API_URL}/users/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    user = UserModel(**response.json())
    return user


def has_permission(headers: Dict[str, str], permission_name: str) -> bool:
    if os.environ.get('DEBUG') == 'True':
        return True
    user = get_request_user(headers)
    if permission_name not in user.permissions:
        return False
    return True
