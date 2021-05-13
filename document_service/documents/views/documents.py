from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api import has_permission
from documents.models import Document, PermissionSet
from documents.permissions import IsAuthenticated
from documents.serializers import AddDocumentSerializer, DocumentSerializer, ChangeDocumentSerializer
from utils import make_pagination_serializer, paginate


@permission_classes([IsAuthenticated])
class DocumentListView(APIView):

    @swagger_auto_schema(request_body=AddDocumentSerializer, responses={'201': DocumentSerializer})
    def post(self, request: Request, *args, **kwargs):
        serializer = AddDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not has_permission(request.headers, PermissionSet.DocumentEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)

        if not (file := request.FILES.get('file')):
            return Response(data={'detail': 'No file received'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.create(
                name=serializer.validated_data.get('name'),
                type=serializer.validated_data.get('type'),
                file=file
            )
        except IntegrityError:
            return Response(data={'detail': 'Wrong document info'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=DocumentSerializer(document, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={'200': make_pagination_serializer(DocumentSerializer)})
    def get(self, request: Request, *args, **kwargs):
        return paginate(
            db_model=Document,
            serializer=DocumentSerializer,
            request=request,
        )


@permission_classes([IsAuthenticated])
class DocumentRetrieveView(APIView):

    @swagger_auto_schema(responses={'200': DocumentSerializer})
    def get(self, request: Request, document_id: int, *args, **kwargs):

        document = Document.objects.filter(id=document_id).first()
        if not document:
            return Response(data={'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=DocumentSerializer(document, context={'request': request}).data)

    @swagger_auto_schema()
    def delete(self, request: Request, document_id: int, *args, **kwargs):
        if not has_permission(request.headers, PermissionSet.DocumentEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)
        document = Document.objects.filter(id=document_id).first()
        if not document:
            return Response(data={'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        document.file.delete()
        document.delete()

        return Response(data={})

    @swagger_auto_schema(request_body=ChangeDocumentSerializer, responses={'201': DocumentSerializer})
    def patch(self, request: Request, document_id: int, *args, **kwargs):
        serializer = ChangeDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not has_permission(request.headers, PermissionSet.DocumentEdit.value):
            return Response(data={'detail': 'User has no permissions for this action'},
                            status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('file')

        document = Document.objects.filter(id=document_id).first()

        if not document:
            return Response(data={'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        document.name = serializer.validated_data.get('name', document.name)
        document.type = serializer.validated_data.get('type', document.type)

        if file:
            document.file.delete()
            document.file = file

        document.save()

        return Response(data=DocumentSerializer(document, context={'request': request}).data,
                        status=status.HTTP_200_OK)
