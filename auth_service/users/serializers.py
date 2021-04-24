from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import login_rule, user_eligible_for_login, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Invite, UserGroup


class DefaultSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        super(self.__class__, self).update(instance, validated_data)

    def create(self, validated_data):
        super(self.__class__, self).create(validated_data)


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


class AddUserSerializer(DefaultSerializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)


class PatchUserSerializer(DefaultSerializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=255, required=False)

    def validate_password(self, value: str) -> str:
        if value:
            return make_password(value)


class InviteSerializer(serializers.ModelSerializer):
    invitee = UserPartSerializer()
    inviter = UserSerializer()

    class Meta:
        model = Invite
        fields = ('id', 'created', 'updated', 'secret_key', 'expiration_date', 'invitee', 'inviter')


class UserWithTokenSerializer(DefaultSerializer):
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


class UserGroupSerializer(serializers.ModelSerializer):
    admin = UserSerializer()
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        fields = ('id', 'created', 'updated', 'name', 'admin', 'users',)


class AddUserToGroupSerializer(DefaultSerializer):
    user_id = serializers.IntegerField(required=True)


class CreateUserGroupSerializer(DefaultSerializer):
    name = serializers.CharField(required=True, max_length=255)


class SwitchUserGroupAdminSerializer(DefaultSerializer):
    new_admin_id = serializers.IntegerField(required=True)


class UserIdQuerySerializer(DefaultSerializer):
    user_id = serializers.IntegerField(required=False)


class LogoutRequestSerializer(DefaultSerializer):
    refresh_token = serializers.CharField(required=True)
