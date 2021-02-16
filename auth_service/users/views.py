from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
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
            return Response(data={'details': 'User not found'}, status=404)
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=200)


class LoginView(TokenViewBase):
    serializer_class = UserWithTokenSerializer
