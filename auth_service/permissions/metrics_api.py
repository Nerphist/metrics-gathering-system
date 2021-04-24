import requests

from auth_service.settings import METRICS_SERVICE_PORT, METRICS_SERVICE_HOST

METRICS_SERVICE_URL = f'http://{METRICS_SERVICE_HOST}:{METRICS_SERVICE_PORT}'


def get_structure():
    response = requests.get(url=f'{METRICS_SERVICE_URL}/metrics/structure/')
    return response.json()
