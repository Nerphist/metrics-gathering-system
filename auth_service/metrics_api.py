import requests

from auth_service.settings import METRICS_SERVICE_PORT, METRICS_SERVICE_HOST

METRICS_SERVICE_URL = f'http://{METRICS_SERVICE_HOST}:{METRICS_SERVICE_PORT}'


def get_structure():
    response = requests.get(url=f'{METRICS_SERVICE_URL}/metrics/structure/')
    return response.json()


def delete_metrics_user(headers, user_id):
    headers = {'Authorization': headers['Authorization']}
    response = requests.delete(url=f'{METRICS_SERVICE_URL}/metrics/responsible_users/users/{user_id}/', headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False
