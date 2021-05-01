from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import login_rule, user_eligible_for_login, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

from permissions.permissions import is_admin
from users.models import User, Invite, UserGroup, ContactInfo
from utils import DefaultSerializer


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ('id', 'created', 'updated', 'user_id', 'name', 'type', 'value', 'notes')


class UserSerializer(serializers.ModelSerializer):
    contact_infos = ContactInfoSerializer(many=True)
    photo_url = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'created', 'updated', 'email', 'is_admin',
                  'password', 'first_name', 'last_name',
                  'contact_infos', 'photo_url', 'activated')
        extra_kwargs = {'password': {'write_only': True}}

    def get_photo_url(self, obj):
        if obj.photo:
            return self.context['request'].build_absolute_uri('/')[:-1] + '/media/' + str(obj.photo)
        else:
            return None

    def get_is_admin(self, obj):
        return is_admin(obj)

    def validate_password(self, value: str) -> str:
        return make_password(value)


class UserPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'activated')


class AddContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ('id', 'created', 'updated', 'name', 'type', 'value', 'notes')

    def validate_type(self, value: str):
        if value.lower() not in ContactInfo.Type.__members__:
            return ContactInfo.Type.messenger.name

        return value.lower()


class PatchContactInfoSerializer(DefaultSerializer):
    name = serializers.CharField(max_length=255, required=False)
    type = serializers.CharField(max_length=255, required=False)
    value = serializers.CharField(max_length=255, required=False)
    notes = serializers.CharField(max_length=255, required=False)


class AddUserSerializer(DefaultSerializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    contact_infos = AddContactInfoSerializer(many=True, required=False)


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
    inviter = UserPartSerializer()

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

        user_serializer = UserSerializer(user, context=self.context)
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
