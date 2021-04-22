from enum import Enum

from django.db import models

# Create your models here.
from users.models import UserGroup
from utils import AbstractCreateUpdateModel


class PermissionGroup(AbstractCreateUpdateModel):
    class Meta:
        index_together = [
            ("entity_type", "entity_id"),
        ]

    class Action(Enum):
        create = 1
        read = 2
        update = 3
        delete = 4

    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, null=False, db_index=True)
    entity_type = models.CharField(max_length=255, null=False, db_index=True)
    entity_id = models.IntegerField(null=False)
    permission_set = models.JSONField(default=list)
