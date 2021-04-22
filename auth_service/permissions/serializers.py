from rest_framework import serializers

from permissions.models import PermissionGroup


class PermissionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionGroup
        fields = ('id', 'created', 'updated', 'entity_type', 'entity_id', 'permission_set', 'user_group_id')
        extra_kwargs = {'password': {'write_only': True}}


class CheckPermissionRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    action = serializers.CharField(max_length=255, required=True)

    def update(self, instance, validated_data):
        super(CheckPermissionRequestSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(CheckPermissionRequestSerializer, self).create(validated_data)


class CheckPermissionResponseSerializer(serializers.Serializer):
    location_groups = serializers.ListField(child=serializers.IntegerField())
    buildings = serializers.ListField(child=serializers.IntegerField())
    floors = serializers.ListField(child=serializers.IntegerField())
    rooms = serializers.ListField(child=serializers.IntegerField())
    devices = serializers.ListField(child=serializers.IntegerField())

    def update(self, instance, validated_data):
        super(CheckPermissionResponseSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(CheckPermissionResponseSerializer, self).create(validated_data)
