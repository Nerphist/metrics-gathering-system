import enum
from enum import Enum
from typing import List

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models, transaction

from users.utils import generate_secret_key, generate_expiration_date
from utils import AbstractCreateUpdateModel


class PermissionSet(enum.Enum):
    LocationRead = 'LocationRead'
    LocationEdit = 'LocationEdit'
    BuildingTypeRead = 'BuildingTypeRead'
    BuildingTypeEdit = 'BuildingTypeEdit'
    BuildingRead = 'BuildingRead'
    BuildingEdit = 'BuildingEdit'
    FloorRead = 'FloorRead'
    FloorEdit = 'FloorEdit'
    RoomRead = 'RoomRead'
    RoomEdit = 'RoomEdit'
    MeterRead = 'MeterRead'
    MeterEdit = 'MeterEdit'
    MeterSnapshotRead = 'MeterSnapshotRead'
    MeterSnapshotEdit = 'MeterSnapshotEdit'
    SupplyContractRead = 'SupplyContractRead'
    SupplyContractEdit = 'SupplyContractEdit'
    TariffRead = 'TariffRead'
    TariffEdit = 'TariffEdit'
    DocumentEdit = 'DocumentEdit'
    DocumentationEdit = 'DocumentationEdit'


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        with transaction.atomic():
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AbstractCreateUpdateModel):
    class Meta(AbstractCreateUpdateModel.Meta):
        db_table = 'users'

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=511)
    activated = models.BooleanField(default=False)
    photo = models.ImageField(null=True, default=None)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self


class Invite(AbstractCreateUpdateModel):
    invitee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='received_invitation')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, related_name='created_invitations')
    secret_key = models.CharField(max_length=511, db_index=True, unique=True, default=generate_secret_key)
    expiration_date = models.DateTimeField(default=generate_expiration_date)


class UserGroup(AbstractCreateUpdateModel):
    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(User, related_name='user_groups')
    admins = models.ManyToManyField(User, related_name='administrated_groups')
    parent_group = models.ForeignKey('UserGroup', on_delete=models.CASCADE, related_name='child_groups', null=True)
    permissions = models.JSONField(null=False, default=list)

    def set_permissions(self, permissions: List[str]):
        permissions_to_be_removed = list(set(self.permissions) - set(permissions))
        if child_groups := self.child_groups.all():
            for group in child_groups:
                group.remove_permissions(permissions_to_be_removed)
        self.permissions = permissions
        self.save()

    def remove_permissions(self, permissions: List[str]):
        self.permissions = list(set(self.permissions) - set(permissions))
        if child_groups := self.child_groups.all():
            for group in child_groups:
                group.remove_permissions(permissions)
        self.save()


class ContactInfo(AbstractCreateUpdateModel):
    class Type(Enum):
        phone = 1
        email = 2
        messenger = 3

    user = models.ForeignKey(User, related_name='contact_infos', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)
