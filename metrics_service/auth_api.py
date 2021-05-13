import os
from datetime import datetime
from os import environ
from typing import Dict

import requests

from request_models.location_requests import UserModel

AUTH_API_HOST = environ.get('AUTH_API_HOST', 'localhost')
AUTH_API_PORT = environ.get('AUTH_API_PORT', '8001')
AUTH_API_URL = f'http://{AUTH_API_HOST}:{AUTH_API_PORT}'

SERVER_API_KEY = os.environ.get('SERVER_API_KEY', '123')


def get_user(user_id: int) -> UserModel:
    response = requests.get(url=f'{AUTH_API_URL}/users/{user_id}/', headers={'Server-Api-Key': SERVER_API_KEY})
    if response.status_code == 404:
        return None
    user = UserModel(**response.json())
    return user


def auth_user(headers: Dict[str, str]) -> UserModel:
    if os.environ.get('DEBUG') == 'True':
        return True
    response = requests.get(url=f'{AUTH_API_URL}/users/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    if response.status_code == 404:
        return False
    user = UserModel(**response.json())
    return user
