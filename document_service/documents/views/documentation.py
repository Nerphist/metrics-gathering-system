from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api import is_admin
from documents.models import DocumentationPart
from documents.permissions import IsAuthenticated
from documents.serializers import AddDocumentationPartSerializer, \
    DocumentationPartSerializer, ChangeDocumentationPartSerializer


@permission_classes([IsAuthenticated])
class DocumentationPartListView(APIView):

    @swagger_auto_schema(request_body=AddDocumentationPartSerializer, responses={'201': DocumentationPartSerializer})
    def post(self, request: Request, *args, **kwargs):
        serializer = AddDocumentationPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not is_admin(request.headers):
            return Response(data={'detail': 'Only admins can create files'}, status=status.HTTP_403_FORBIDDEN)

        if not (file := request.FILES.get('file')):
            return Response(data={'detail': 'No file received'}, status=status.HTTP_400_BAD_REQUEST)

        existing_documentations = {dp.order: dp for dp in DocumentationPart.objects.all()}

        order = serializer.validated_data.get('order')
        if order <= 0:
            return Response(data={'detail': 'Order must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

        if not existing_documentations:
            order = 1
        else:
            max_order = max(list(existing_documentations.keys()))
            if order > max_order:
                order = max_order + 1
            else:
                need_to_be_pushed = range(max_order, order - 1, -1)
                for index in need_to_be_pushed:
                    existing_documentations[index].order += 1
                    existing_documentations[index].save()

        try:
            documentation_part = DocumentationPart.objects.create(
                name=serializer.validated_data.get('name'),
                order=order,
                file=file
            )
        except IntegrityError:
            return Response(data={'detail': 'Wrong documentation_part info'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=DocumentationPartSerializer(documentation_part, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': DocumentationPartSerializer(many=True)})
    def get(self, request: Request, *args, **kwargs):

        documentation_parts = DocumentationPart.objects.all()
        return Response(
            data=[DocumentationPartSerializer(documentation_part, context={'request': request}).data for
                  documentation_part in documentation_parts])


@permission_classes([IsAuthenticated])
class DocumentationPartRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': DocumentationPartSerializer})
    def get(self, request: Request, documentation_part_id: int, *args, **kwargs):

        documentation_part = DocumentationPart.objects.filter(id=documentation_part_id).first()
        if not documentation_part:
            return Response(data={'detail': 'DocumentationPart not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=DocumentationPartSerializer(documentation_part, context={'request': request}).data)

    @swagger_auto_schema()
    def delete(self, request: Request, documentation_part_id: int, *args, **kwargs):

        documentation_part = DocumentationPart.objects.filter(id=documentation_part_id).first()
        if not documentation_part:
            return Response(data={'detail': 'DocumentationPart not found'}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin(request.headers):
            return Response(data={'detail': 'User cannot delete this documentation_part'},
                            status=status.HTTP_403_FORBIDDEN)

        order = documentation_part.order
        documentation_part.file.delete()
        documentation_part.delete()

        existing_documentations = DocumentationPart.objects.filter(order__gt=order).order_by('order')

        for dp in existing_documentations:
            dp.order -= 1
            dp.save()

        return Response(data={})

    @swagger_auto_schema(request_body=ChangeDocumentationPartSerializer, responses={'201': DocumentationPartSerializer})
    def patch(self, request: Request, documentation_part_id: int, *args, **kwargs):
        serializer = ChangeDocumentationPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not is_admin(request.headers):
            return Response(data={'detail': 'Only admins can change files'}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('file')

        documentation_part = DocumentationPart.objects.filter(id=documentation_part_id).first()

        if not documentation_part:
            return Response(data={'detail': 'DocumentationPart not found'}, status=status.HTTP_404_NOT_FOUND)

        order = serializer.validated_data.get('order')
        if order != documentation_part.order:
            if order <= 0:
                return Response(data={'detail': 'Order must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

            existing_documentations = {dp.order: dp for dp in DocumentationPart.objects.filter().all()}
            old_order = documentation_part.order

            if order < old_order:
                need_to_be_pushed = range(old_order, order - 1, -1)
                for index in need_to_be_pushed:
                    existing_documentations[index].order += 1
                    existing_documentations[index].save()
            else:
                max_order = max(list(existing_documentations.keys()))
                order = min(order, max_order)

                need_to_be_pushed = range(order, old_order - 1, -1)
                for index in need_to_be_pushed:
                    existing_documentations[index].order -= 1
                    existing_documentations[index].save()

        documentation_part.name = serializer.validated_data.get('name', documentation_part.name)
        documentation_part.order = order

        if file:
            documentation_part.file.delete()
            documentation_part.file = file

        documentation_part.save()

        return Response(data=DocumentationPartSerializer(documentation_part, context={'request': request}).data,
                        status=status.HTTP_200_OK)
