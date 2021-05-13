from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api import has_permission
from documents.models import SupplyContract, PermissionSet
from documents.permissions import IsAuthenticated
from documents.serializers import AddSupplyContractSerializer, SupplyContractSerializer, ChangeSupplyContractSerializer
from utils import paginate, make_pagination_serializer


@permission_classes([IsAuthenticated])
class SupplyContractListView(APIView):

    @swagger_auto_schema(request_body=AddSupplyContractSerializer, responses={'201': SupplyContractSerializer})
    def post(self, request: Request, *args, **kwargs):
        serializer = AddSupplyContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not has_permission(request.headers, PermissionSet.SupplyContractEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)

        if not (file := request.FILES.get('file')):
            return Response(data={'detail': 'No file received'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supply_contract = SupplyContract.objects.create(
                **serializer.validated_data,
                file=file
            )
        except IntegrityError:
            return Response(data={'detail': 'Wrong supply_contract info'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=SupplyContractSerializer(supply_contract, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': make_pagination_serializer(SupplyContractSerializer)})
    def get(self, request: Request, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.SupplyContractRead.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return paginate(
            db_model=SupplyContract,
            serializer=SupplyContractSerializer,
            request=request,
        )


@permission_classes([IsAuthenticated])
class SupplyContractRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': SupplyContractSerializer})
    def get(self, request: Request, supply_contract_id: int, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.SupplyContractRead.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)

        supply_contract = SupplyContract.objects.filter(id=supply_contract_id).first()
        if not supply_contract:
            return Response(data={'detail': 'SupplyContract not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=SupplyContractSerializer(supply_contract, context={'request': request}).data)

    @swagger_auto_schema()
    def delete(self, request: Request, supply_contract_id: int, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.SupplyContractEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        supply_contract = SupplyContract.objects.filter(id=supply_contract_id).first()
        if not supply_contract:
            return Response(data={'detail': 'SupplyContract not found'}, status=status.HTTP_404_NOT_FOUND)

        supply_contract.file.delete()
        supply_contract.delete()

        return Response(data={})

    @swagger_auto_schema(request_body=ChangeSupplyContractSerializer, responses={'201': SupplyContractSerializer})
    def patch(self, request: Request, supply_contract_id: int, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.SupplyContractEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = ChangeSupplyContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = request.FILES.get('file')

        supply_contract = SupplyContract.objects.filter(id=supply_contract_id).first()

        if not supply_contract:
            return Response(data={'detail': 'SupplyContract not found'}, status=status.HTTP_404_NOT_FOUND)

        supply_contract.type = serializer.validated_data.get('type', supply_contract.type)
        supply_contract.number = serializer.validated_data.get('number', supply_contract.number)
        supply_contract.notes = serializer.validated_data.get('notes', supply_contract.notes)
        supply_contract.expiration_date = serializer.validated_data.get('expiration_date',
                                                                        supply_contract.expiration_date)
        supply_contract.start_date = serializer.validated_data.get('start_date', supply_contract.start_date)

        if file:
            supply_contract.file.delete()
            supply_contract.file = file

        supply_contract.save()

        return Response(data=SupplyContractSerializer(supply_contract, context={'request': request}).data,
                        status=status.HTTP_200_OK)
