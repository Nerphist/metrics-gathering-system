from django.db import models

from utils import AbstractCreateUpdateModel


class Document(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

    file = models.FileField(null=True, default=None)
