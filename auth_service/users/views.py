from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from users.models import User
from users.serializers import UserSerializer, UserWithTokenSerializer


class RegisterView(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request: Request, *args, **kwargs):
    ser = UserSerializer(request.user)
    return Response(ser.data)
