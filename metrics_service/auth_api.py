from dataclasses import dataclass
from os import environ

import requests

AUTH_API_URL = environ.get('AUTH_API_URL', 'localhost:8001')


@dataclass
class User:
    id: int
    email: str


def get_user(user_id: int) -> User:
    response = requests.get(url=f'http://{AUTH_API_URL}/get-user/{user_id}/')
    if response.status_code == 404:
        return None
    user = User(**response.json())
    return user
