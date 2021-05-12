from enum import Enum

from django.db import models

# Create your models here.
from users.models import UserGroup
from utils import AbstractCreateUpdateModel


class PermissionGroup(AbstractCreateUpdateModel):
    pass
