import enum

from django.db import models

from utils import AbstractCreateUpdateModel


class PermissionSet(enum.Enum):
    SupplyContractRead = 'SupplyContractRead'
    SupplyContractEdit = 'SupplyContractEdit'
    TariffRead = 'TariffRead'
    TariffEdit = 'TariffEdit'
    DocumentEdit = 'DocumentEdit'
    DocumentationEdit = 'DocumentationEdit'


class DocumentType(models.TextChoices):
    Gas = 'Gas'
    Water = 'Water'
    Electricity = 'Electricity'
    Heat = 'Heat'


class Document(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=False)

    file = models.FileField(null=False)


class DocumentationPart(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, null=False)
    order = models.IntegerField(db_index=True)

    file = models.FileField(null=False)


class SupplyContract(AbstractCreateUpdateModel):
    number = models.IntegerField()
    type = models.CharField(choices=DocumentType.choices, max_length=255, null=False)
    notes = models.CharField(max_length=255)

    file = models.FileField(null=False)

    start_date = models.DateTimeField(null=True, default=None)
    expiration_date = models.DateTimeField(null=True, default=None)


class Tariff(AbstractCreateUpdateModel):
    type = models.CharField(choices=DocumentType.choices, max_length=255, null=False)
    notes = models.CharField(max_length=255)

    file = models.FileField(null=True, default=None)

    enacted_since = models.DateTimeField(null=True, default=None)
    commercial_price = models.DecimalField(null=True, default=None, max_digits=30, decimal_places=2)
    reduced_price = models.DecimalField(null=True, default=None, max_digits=30, decimal_places=2)
    residential_price = models.DecimalField(null=True, default=None, max_digits=30, decimal_places=2)
