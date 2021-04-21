from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from users.models import User, Invite
from users.serializers import UserSerializer, UserWithTokenSerializer, AddUserSerializer, InviteSerializer
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

    def post(self, request: Request, secret_key: str, *args, **kwargs):
        invite = Invite.objects.filter(secret_key=secret_key).first()
        if not invite:
            return Response(data={'detail': 'Invite not found'}, status=404)
        if invite.user.activated:
            return Response(data={'detail': 'User is already activated'}, status=400)
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(data={'detail': 'email and password fields are required'}, status=400)
        user = invite.user
        user.email = email
        user.password = make_password(password)
        user.activated = True
        user.save()
        serializer = UserSerializer(user)
        return Response(data=serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request: Request, *args, **kwargs):
    ser = UserSerializer(request.user)
    return Response(ser.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_created_invitations(request: Request, *args, **kwargs):
    invites = Invite.objects.filter(inviter=request.user).all()
    return Response(data=[InviteSerializer(invite).data for invite in invites])


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # to be changed to admin
def add_user(request: Request, *args, **kwargs):
    serializer = AddUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = generate_random_email()
    password = make_password(generate_random_password())
    user = User.objects.create_user(email=email, password=password, **serializer.data)

    invite = Invite.objects.create(invitee=user, inviter=request.user)
    return Response(data=InviteSerializer(invite).data, status=201)
