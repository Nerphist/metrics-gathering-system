from django.contrib.auth.hashers import make_password
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from permissions.permissions import IsAdmin
from users.models import User, Invite, UserGroup
from users.serializers import UserSerializer, UserWithTokenSerializer, AddUserSerializer, InviteSerializer, \
    AddUserToGroupSerializer, UserGroupSerializer, CreateUserGroupSerializer, SwitchUserGroupAdminSerializer
from users.utils import generate_random_email, generate_random_password


class GetUserView(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        return User.objects.filter(id=user_id).first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(data={'detail': 'User not found'}, status=404)
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=200)


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
            return Response(data={'detail': 'Invite not found'}, status=404)
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=200)


class ConfirmInviteView(APIView):

    @swagger_auto_schema(request_body=UserWithTokenSerializer, responses={'200': UserSerializer})
    def post(self, request: Request, secret_key: str, *args, **kwargs):
        invite = Invite.objects.filter(secret_key=secret_key).first()
        if not invite:
            return Response(data={'detail': 'Invite not found'}, status=404)
        if invite.invitee.activated:
            return Response(data={'detail': 'User is already activated'}, status=400)
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(data={'detail': 'email and password fields are required'}, status=400)
        user = invite.invitee
        user.email = email
        user.password = make_password(password)
        user.activated = True
        user.save()
        serializer = UserSerializer(user)
        return Response(data=serializer.data)


class UserGroupListView(APIView):

    @swagger_auto_schema(request_body=CreateUserGroupSerializer, responses={'201': UserGroupSerializer})
    @permission_classes([IsAuthenticated, IsAdmin])
    def post(self, request: Request, *args, **kwargs):
        serializer = CreateUserGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_group = UserGroup.objects.create(name=serializer.validated_data.get('name'), admin=request.user)

        return Response(data=UserGroupSerializer(user_group).data, status=201)

    @swagger_auto_schema(responses={'200': UserGroupSerializer(many=True)})
    @permission_classes([IsAuthenticated])
    def get(self, request: Request, *args, **kwargs):
        query = UserGroup.objects
        if IsAdmin().has_permission(request):
            groups = query.all()
        else:
            groups = request.user.user_groups

        return Response(data=[UserGroupSerializer(user_group) for user_group in groups])


class UserGroupRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': UserGroupSerializer})
    @permission_classes([IsAuthenticated])
    def get(self, request: Request, user_group_id: int, *args, **kwargs):

        user_group = UserGroup.objects.filter(id=user_group_id).first()
        if not user_group:
            return Response(data={'detail': 'User group not found'}, status=404)
        if not IsAdmin().has_permission(request) and user_group not in request.user.user_groups:
            return Response(data={'detail': 'User cannot view this group'}, status=403)

        return Response(data=UserGroupSerializer(user_group))

    @swagger_auto_schema
    @permission_classes([IsAuthenticated])
    def delete(self, request: Request, user_group_id: int, *args, **kwargs):

        user_group = UserGroup.objects.filter(id=user_group_id).first()
        if not user_group:
            return Response(data={'detail': 'User group not found'}, status=404)
        if not IsAdmin().has_permission(request) and user_group.admin != request.user:
            return Response(data={'detail': 'User cannot delete this group'}, status=403)

        user_group.delete()

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
    user = User.objects.create_user(email=email, password=password, **serializer.data)

    invite = Invite.objects.create(invitee=user, inviter=request.user)
    return Response(data=InviteSerializer(invite).data, status=201)


@swagger_auto_schema(method='POST', request_body=AddUserToGroupSerializer, responses={'200': UserGroupSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_group(request: Request, user_group_id: int, *args, **kwargs):
    serializer = AddUserToGroupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.filter(id=serializer.validated_data.get('user_id')).first()
    if not user:
        return Response(data={'detail': 'User not found'}, status=404)
    user_group = UserGroup.objects.filter(id=user_group_id).first()
    if not user_group:
        return Response(data={'detail': 'User group not found'}, status=404)

    if not IsAdmin().has_permission(request) and user_group.admin != request.user:
        return Response(data={'detail': 'You must be a group admin to add users to it'}, status=403)

    if user not in user_group.users:
        user_group.users.add(user)

    return Response(data=UserGroupSerializer(user_group).data, status=200)


@swagger_auto_schema(method='POST', request_body=SwitchUserGroupAdminSerializer, responses={'200': UserGroupSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_user_group_admin(request: Request, user_group_id: int, *args, **kwargs):
    serializer = SwitchUserGroupAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_group = UserGroup.objects.filter(id=user_group_id).first()
    if not user_group:
        return Response(data={'detail': 'User group not found'}, status=404)
    new_admin = User.objects.filter(id=serializer.validated_data.get('new_admin_id')).first()
    if not new_admin:
        return Response(data={'detail': 'User not found'}, status=404)

    user_group.admin = new_admin
    if new_admin not in user_group.users:
        user_group.users.add(new_admin)

    return Response(data=UserGroupSerializer(user_group).data, status=200)
