from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import login_rule, user_eligible_for_login, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Invite, UserGroup


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'created', 'updated', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value: str) -> str:
        return make_password(value)


class UserPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class AddUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)

    def update(self, instance, validated_data):
        super(AddUserSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(AddUserSerializer, self).create(validated_data)


class InviteSerializer(serializers.ModelSerializer):
    invitee = UserPartSerializer()
    inviter = UserSerializer()

    class Meta:
        model = Invite
        fields = ('id', 'created', 'updated', 'secret_key', 'expiration_date', 'invitee', 'inviter')


class UserWithTokenSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField()

    @classmethod
    def get_token(cls, user) -> RefreshToken:
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = authenticate(**authenticate_kwargs)

        if not getattr(login_rule, user_eligible_for_login)(user):
            raise AuthenticationFailed()

        data = {}
        refresh_token = self.get_token(user)
        data['refresh'] = str(refresh_token)
        data['access'] = str(refresh_token.access_token)

        user_serializer = UserSerializer(user)
        data.update(user_serializer.data)

        return data

    def update(self, instance, validated_data):
        super(UserWithTokenSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(UserWithTokenSerializer, self).create(validated_data)


class UserGroupSerializer(serializers.ModelSerializer):
    admin = UserSerializer()
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        fields = ('id', 'created', 'updated', 'name', 'admin', 'users',)


class AddUserToGroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        super(AddUserToGroupSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(AddUserToGroupSerializer, self).create(validated_data)


class CreateUserGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=255)

    def update(self, instance, validated_data):
        super(CreateUserGroupSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(CreateUserGroupSerializer, self).create(validated_data)


class SwitchUserGroupAdminSerializer(serializers.Serializer):
    new_admin_id = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        super(SwitchUserGroupAdminSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(SwitchUserGroupAdminSerializer, self).create(validated_data)
