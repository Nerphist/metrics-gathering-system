from django.db import models

from utils import AbstractCreateUpdateModel


class Document(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=False)

    file = models.FileField(null=False)


class DocumentationPart(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, null=False)
    order = models.IntegerField(db_index=True)

    file = models.FileField(null=False)


class SupplyContract(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, null=False)
    number = models.IntegerField()
    type = models.CharField(max_length=255, null=False)
    notes = models.CharField(max_length=255)

    file = models.FileField(null=False)

    start_date = models.DateTimeField(null=True, default=None)
    expiration_date = models.DateTimeField(null=True, default=None)
