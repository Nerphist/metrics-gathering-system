from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from permissions.models import PermissionGroup
from permissions.serializers import CheckPermissionRequestSerializer, CheckPermissionResponseSerializer
from users.models import User


@swagger_auto_schema(method='POST', request_body=CheckPermissionRequestSerializer,
                     responses={'200': CheckPermissionResponseSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def get_permissions(request: Request, *args, **kwargs):
    serializer = CheckPermissionRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.get(id=serializer.validated_data.get('user_id'))
    user_groups = user.user_groups.all()
    action = serializer.validated_data.get('action')

    permissions = {str(entity): [] for entity in PermissionGroup.EntityTypes.__members__}

    for user_group in user_groups:
        for permission_group in user_group.permission_groups.all():
            if action.lower() in permission_group.permission_set:
                permissions[permission_group.entity_type].append(permission_group.entity_id)

    return Response(data=permissions, status=200)
