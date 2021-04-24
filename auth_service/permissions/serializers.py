from rest_framework import serializers

from permissions.models import PermissionGroup
from utils import DefaultSerializer


class PermissionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionGroup
        fields = ('id', 'created', 'updated', 'entity_type', 'entity_id', 'permission_set', 'user_group_id')
        extra_kwargs = {'password': {'write_only': True}}


class GetPermissionsRequestQuerySerializer(DefaultSerializer):
    user_id = serializers.IntegerField(required=False)


class AddPermissionsRequestSerializer(DefaultSerializer):
    user_group_id = serializers.IntegerField(required=True)
    entity_id = serializers.IntegerField(required=True)
    entity_type = serializers.ChoiceField(choices=[str(p) for p in PermissionGroup.EntityTypes.__members__],
                                          required=True)
    actions = serializers.ListField(child=serializers.CharField(), required=True)


class PermissionsSerializer(DefaultSerializer):
    # location_groups = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
    buildings = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
    floors = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
    rooms = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
    devices = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))


class GetPermissionsResponseSerializer(DefaultSerializer):
    is_admin = serializers.BooleanField()
    permissions = PermissionsSerializer()
