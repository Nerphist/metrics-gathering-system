from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.views import TokenViewBase

from auth_service.settings import ADMIN_GROUP_NAME
from permissions.permissions import is_admin, is_super_admin, ServerApiKeyAuthorized
from users.models import User, Invite, UserGroup, ContactInfo
from users.serializers import UserSerializer, UserWithTokenSerializer, AddUserSerializer, InviteSerializer, \
    AddUserToGroupSerializer, UserGroupSerializer, CreateUserGroupSerializer, SwitchUserGroupAdminSerializer, \
    PatchUserSerializer, UserIdQuerySerializer, ContactInfoSerializer, AddContactInfoSerializer
from users.utils import generate_random_email, generate_random_password


@permission_classes([IsAuthenticated])
class LogoutView(APIView):

    @swagger_auto_schema()
    def post(self, request):
        for token in request.user.outstandingtoken_set.all():
            BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


@permission_classes([IsAuthenticated | ServerApiKeyAuthorized])
class SingleUserView(APIView):

    @swagger_auto_schema(responses={'200': UserSerializer})
    def get(self, request: Request, user_id: int, *args, **kwargs):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(data={'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user, context={'request': request}).data)

    @swagger_auto_schema(request_body=PatchUserSerializer, responses={'200': UserSerializer})
    def patch(self, request: Request, user_id: int, *args, **kwargs):
        serializer = PatchUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(data={'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user:
            if not is_admin(request.user):
                return Response(data={'detail': 'Only admin can do it'}, status=status.HTTP_403_FORBIDDEN)
            elif not is_super_admin(request.user):
                return Response(data={'detail': 'Only superadmin can change admin\'s information'},
                                status=status.HTTP_403_FORBIDDEN)

        user.first_name = serializer.validated_data.get('first_name', user.first_name)
        user.last_name = serializer.validated_data.get('last_name', user.last_name)
        user.email = serializer.validated_data.get('email', user.email)
        user.password = serializer.validated_data.get('password', user.password)

        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            user.photo = photo_file
            print(user.photo.path)
        user.save()
        return Response(UserSerializer(user, context={'request': request}).data)


@permission_classes([IsAuthenticated])
class GetAllUsersView(ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', '')
        return User.objects.filter(Q(first_name__contains=name) | Q(last_name__contains=name)).all()


class LoginView(TokenViewBase):
    serializer_class = UserWithTokenSerializer


class GetByInviteView(RetrieveModelMixin, GenericViewSet):
    serializer_class = InviteSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        secret_key = self.kwargs['secret_key']
        return Invite.objects.filter(secret_key=secret_key).first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(data={'detail': 'Invite not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ConfirmInviteView(APIView):

    @swagger_auto_schema(request_body=UserWithTokenSerializer, responses={'200': UserSerializer})
    def post(self, request: Request, secret_key: str, *args, **kwargs):
        invite = Invite.objects.filter(secret_key=secret_key).first()
        if not invite:
            return Response(data={'detail': 'Invite not found'}, status=status.HTTP_404_NOT_FOUND)
        if invite.invitee.activated:
            return Response(data={'detail': 'User is already activated'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(data={'detail': 'email and password fields are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = invite.invitee
        user.email = email
        user.password = make_password(password)
        user.activated = True
        user.save()
        serializer = UserSerializer(user)
        return Response(data=serializer.data)


@permission_classes([IsAuthenticated])
class UserGroupListView(APIView):

    @swagger_auto_schema(request_body=CreateUserGroupSerializer, responses={'201': UserGroupSerializer})
    def post(self, request: Request, *args, **kwargs):
        if not is_admin(request.user):
            return Response(data={'detail': 'Only admin can add groups'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateUserGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_group = UserGroup.objects.create(name=serializer.validated_data.get('name'), admin=request.user)
            user_group.users.add(request.user)
        except IntegrityError:
            return Response(data={'detail': 'Such group already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=UserGroupSerializer(user_group).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': UserGroupSerializer(many=True)}, query_serializer=UserIdQuerySerializer)
    def get(self, request: Request, *args, **kwargs):
        query = UserGroup.objects

        if user_id := int(request.query_params.get('user_id', 0)):
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response(data={'detail': 'Wrong user_id'}, status=status.HTTP_400_BAD_REQUEST)
            groups = user.user_groups.all()
        else:
            groups = query.all()
        return Response(data=[UserGroupSerializer(user_group).data for user_group in groups])


@permission_classes([IsAuthenticated])
class UserGroupRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': UserGroupSerializer})
    def get(self, request: Request, user_group_id: int, *args, **kwargs):

        user_group = UserGroup.objects.filter(id=user_group_id).first()
        if not user_group:
            return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin(request.user) and user_group not in request.user.user_groups.all():
            return Response(data={'detail': 'User cannot view this group'}, status=status.HTTP_403_FORBIDDEN)

        return Response(data=UserGroupSerializer(user_group).data)

    @swagger_auto_schema()
    def delete(self, request: Request, user_group_id: int, *args, **kwargs):

        user_group = UserGroup.objects.filter(id=user_group_id).first()
        if not user_group:
            return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin(request.user) and user_group.admin != request.user:
            return Response(data={'detail': 'User cannot delete this group'}, status=status.HTTP_403_FORBIDDEN)

        if user_group.name == ADMIN_GROUP_NAME:
            return Response(data={'detail': 'Impossible to delete the admin group'}, status=status.HTTP_400_BAD_REQUEST)

        user_group.delete()

        return Response(data={})


@permission_classes([IsAuthenticated])
class ContactInfoListView(APIView):

    @swagger_auto_schema(request_body=AddContactInfoSerializer, responses={'201': ContactInfoSerializer})
    def post(self, request: Request, *args, **kwargs):

        serializer = AddContactInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            contact_info = ContactInfo.objects.create(
                name=serializer.validated_data.get('name'),
                type=serializer.validated_data.get('type'),
                value=serializer.validated_data.get('name'),
                notes=serializer.validated_data.get('notes'),
                user=request.user,
            )
        except IntegrityError:
            return Response(data={'detail': 'Wrong contact info'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=ContactInfoSerializer(contact_info).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': ContactInfoSerializer(many=True)}, query_serializer=UserIdQuerySerializer)
    def get(self, request: Request, *args, **kwargs):
        if user_id := int(request.query_params.get('user_id', 0)):
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response(data={'detail': 'Wrong user_id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user

        contact_infos = user.contact_infos.all()
        return Response(data=[ContactInfoSerializer(contact_info).data for contact_info in contact_infos])


@permission_classes([IsAuthenticated])
class ContactInfoRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': ContactInfoSerializer})
    def get(self, request: Request, contact_info_id: int, *args, **kwargs):

        contact_info = ContactInfo.objects.filter(id=contact_info_id).first()
        if not contact_info:
            return Response(data={'detail': 'Contact info group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin(request.user) and contact_info not in request.user.contact_infos.all():
            return Response(data={'detail': 'User cannot view this contact info'}, status=status.HTTP_403_FORBIDDEN)

        return Response(data=ContactInfoSerializer(contact_info).data)

    @swagger_auto_schema()
    def delete(self, request: Request, contact_info_id: int, *args, **kwargs):

        contact_info = ContactInfo.objects.filter(id=contact_info_id).first()
        if not contact_info:
            return Response(data={'detail': 'Contact info not found'}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin(request.user) and contact_info.admin != request.user:
            return Response(data={'detail': 'User cannot delete this contact info'}, status=status.HTTP_403_FORBIDDEN)

        contact_info.delete()

        return Response(data={})


@swagger_auto_schema(method='GET', responses={'200': UserSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request: Request, *args, **kwargs):
    ser = UserSerializer(request.user)
    return Response(ser.data)


@swagger_auto_schema(method='GET', responses={'200': InviteSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_created_invitations(request: Request, *args, **kwargs):
    invites = Invite.objects.filter(inviter=request.user).all()
    return Response(data=[InviteSerializer(invite).data for invite in invites])


@swagger_auto_schema(method='POST', request_body=AddUserSerializer, responses={'201': InviteSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user(request: Request, *args, **kwargs):
    serializer = AddUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = generate_random_email()
    password = make_password(generate_random_password())
    contact_info = serializer.validated_data.get('contact_info')
    user = User.objects.create_user(email=email, password=password,
                                    first_name=serializer.validated_data.get('first_name'),
                                    last_name=serializer.validated_data.get('last_name'))

    if contact_info:
        contact_info['user_id'] = user.id
        ContactInfo.objects.create(**contact_info)

    invite = Invite.objects.create(invitee=user, inviter=request.user)
    return Response(data=InviteSerializer(invite).data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='POST', request_body=AddUserToGroupSerializer, responses={'200': UserGroupSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_group(request: Request, user_group_id: int, *args, **kwargs):
    serializer = AddUserToGroupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.filter(id=serializer.validated_data.get('user_id')).first()
    if not user:
        return Response(data={'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    user_group = UserGroup.objects.filter(id=user_group_id).first()
    if not user_group:
        return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)

    if not is_admin(request.user) and user_group.admin != request.user:
        return Response(data={'detail': 'You must be a group admin to add users to it'},
                        status=status.HTTP_403_FORBIDDEN)

    if user not in user_group.users.all():
        user_group.users.add(user)

    return Response(data=UserGroupSerializer(user_group).data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='POST', request_body=SwitchUserGroupAdminSerializer, responses={'200': UserGroupSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_user_group_admin(request: Request, user_group_id: int, *args, **kwargs):
    serializer = SwitchUserGroupAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_group = UserGroup.objects.filter(id=user_group_id).first()
    if not user_group:
        return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)
    new_admin = User.objects.filter(id=serializer.validated_data.get('new_admin_id')).first()
    if not new_admin:
        return Response(data={'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if user_group.name == ADMIN_GROUP_NAME:
        if not is_super_admin(request.user):
            return Response(data={'detail': 'Only super admin can change this role'}, status=status.HTTP_403_FORBIDDEN)

    if is_admin(request.user) or request.user == user_group.admin:
        user_group.admin = new_admin
        if new_admin not in user_group.users.all():
            user_group.users.add(new_admin)
    else:
        return Response(data={'detail': 'Only admin can remove others from the group'},
                        status=status.HTTP_403_FORBIDDEN)

    return Response(data=UserGroupSerializer(user_group).data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='DELETE', responses={'200': UserGroupSerializer})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_group(request: Request, user_group_id: int, user_to_remove_id: int, *args, **kwargs):
    user_group: UserGroup = UserGroup.objects.filter(id=user_group_id).first()
    if not user_group:
        return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)

    user_to_remove = User.objects.filter(id=user_to_remove_id).first()
    if not user_to_remove:
        return Response(data={'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if user_group.name == ADMIN_GROUP_NAME:
        if user_to_remove == user_group.admin:
            return Response(data={'detail': 'It is impossible ro remove super admin from the admin group'},
                            status=status.HTTP_403_FORBIDDEN)
        if not is_super_admin(request.user):
            return Response(data={'detail': 'Only super admin can remove from admin group'},
                            status=status.HTTP_403_FORBIDDEN)

    if is_admin(request.user) or request.user == user_group.admin:
        user_group.users.remove(user_to_remove)
        if user_to_remove == user_group.admin:
            user_group.admin = request.user
            user_group.save()
            if request.user not in user_group.users.all():
                user_group.users.add(request.user)
    else:
        return Response(data={'detail': 'Only admin can remove others from the group'},
                        status=status.HTTP_403_FORBIDDEN)

    return Response(data=UserGroupSerializer(user_group).data, status=status.HTTP_200_OK)
