import random
import string
from datetime import datetime

from auth_service.settings import INVITATION_EXPIRATION_TIME


def _generate_random_string(length=100):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(100))


def generate_random_email():
    return _generate_random_string(30) + '@nonvalid.com'


def generate_random_password():
    return _generate_random_string(100)


def generate_secret_key():
    return _generate_random_string(255)


def generate_expiration_date():
    return datetime.utcnow() + INVITATION_EXPIRATION_TIME


def is_in_parent_group(user, current_group):
    parent_groups = set()
    while current_group.parent_group:
        parent_groups.add(current_group.parent_group)
        current_group = current_group.parent_group

    if parent_groups.intersection(set(user.user_groups.all())):
        return True

    return False


def is_admin_of_parent_group(user, current_group):
    parent_groups = set()
    while current_group.parent_group:
        parent_groups.add(current_group.parent_group)
        current_group = current_group.parent_group

    if parent_groups.intersection(set(user.administrated_groups.all())):
        return True

    return False
