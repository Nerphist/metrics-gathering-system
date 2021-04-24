from dataclasses import dataclass
from os import environ
from typing import Dict

import requests

AUTH_API_HOST = environ.get('AUTH_API_HOST', 'localhost')
AUTH_API_PORT = environ.get('AUTH_API_PORT', '8001')
AUTH_API_URL = f'http://{AUTH_API_HOST}:{AUTH_API_PORT}'


@dataclass
class User:
    id: int
    email: str
    first_name: str
    last_name: str


def get_user(user_id: int) -> User:
    response = requests.get(url=f'{AUTH_API_URL}/users/{user_id}/')
    if response.status_code == 404:
        return None
    user = User(**response.json())
    return user


def auth_user(headers: Dict[str, str]) -> bool:
    response = requests.get(url=f'{AUTH_API_URL}/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    return response.status_code == 200
