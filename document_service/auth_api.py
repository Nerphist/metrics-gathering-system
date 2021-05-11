import os
from typing import Dict

import requests

from document_service.settings import AUTH_SERVICE_HOST, AUTH_SERVICE_PORT

AUTH_API_URL = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"

SERVER_API_KEY = os.environ.get('SERVER_API_KEY', '123')


def auth_user(headers: Dict[str, str]) -> bool:
    if os.environ.get('DEBUG') == 'True':
        return True
    response = requests.get(url=f'{AUTH_API_URL}/users/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    return response.status_code == 200


def is_admin(headers: Dict[str, str]) -> bool:
    return True  # to be changed after permissions added
    if os.environ.get('DEBUG') == 'True':
        return True
    response = requests.get(url=f'{AUTH_API_URL}/users/auth-user/',
                            headers={k.capitalize(): v for k, v in headers.items()})
    return response.json()['is_admin']
