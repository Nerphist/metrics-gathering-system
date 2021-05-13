from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api import has_permission
from documents.models import Tariff, PermissionSet
from documents.permissions import IsAuthenticated
from documents.serializers import AddTariffSerializer, TariffSerializer, ChangeTariffSerializer
from utils import paginate, make_pagination_serializer


@permission_classes([IsAuthenticated])
class TariffListView(APIView):

    @swagger_auto_schema(request_body=AddTariffSerializer, responses={'201': TariffSerializer})
    def post(self, request: Request, *args, **kwargs):
        serializer = AddTariffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not has_permission(request.headers, PermissionSet.TariffEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            tariff = Tariff.objects.create(
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(data={'detail': 'Wrong tariff info'}, status=status.HTTP_400_BAD_REQUEST)

        if file := request.FILES.get('file'):
            tariff.file = file
            tariff.save()

        return Response(data=TariffSerializer(tariff, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': make_pagination_serializer(TariffSerializer)})
    def get(self, request: Request, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.TariffRead.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return paginate(
            db_model=Tariff,
            serializer=TariffSerializer,
            request=request,
        )


@permission_classes([IsAuthenticated])
class TariffRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': TariffSerializer})
    def get(self, request: Request, tariff_id: int, *args, **kwargs):

        if not has_permission(request.headers, PermissionSet.TariffRead.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        tariff = Tariff.objects.filter(id=tariff_id).first()
        if not tariff:
            return Response(data={'detail': 'Tariff not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=TariffSerializer(tariff, context={'request': request}).data)

    @swagger_auto_schema()
    def delete(self, request: Request, tariff_id: int, *args, **kwargs):

        if not has_permission(request.headers, PermissionSet.TariffEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        tariff = Tariff.objects.filter(id=tariff_id).first()
        if not tariff:
            return Response(data={'detail': 'Tariff not found'}, status=status.HTTP_404_NOT_FOUND)

        tariff.file.delete()
        tariff.delete()

        return Response(data={})

    @swagger_auto_schema(request_body=ChangeTariffSerializer, responses={'201': TariffSerializer})
    def patch(self, request: Request, tariff_id: int, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.TariffEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = ChangeTariffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = request.FILES.get('file')

        tariff = Tariff.objects.filter(id=tariff_id).first()

        if not tariff:
            return Response(data={'detail': 'Tariff not found'}, status=status.HTTP_404_NOT_FOUND)

        for k, v in serializer.validated_data.items():
            if v:
                setattr(tariff, k, v)

        if file:
            tariff.file.delete()
            tariff.file = file

        tariff.save()

        return Response(data=TariffSerializer(tariff, context={'request': request}).data,
                        status=status.HTTP_200_OK)
