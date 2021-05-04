from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import login_rule, user_eligible_for_login, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken
from hurry.filesize import size

from documents.models import Document, DocumentationPart, SupplyContract
from utils import DefaultSerializer


class FileSerializer(DefaultSerializer):
    file_size = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    def get_file_size(self, obj):
        return size(obj.file.size)

    def get_file_name(self, obj):
        return obj.file.name

    def get_file_url(self, obj):
        return self.context['request'].build_absolute_uri('/')[:-1] + '/media/' + str(obj.file)


class DocumentSerializer(serializers.ModelSerializer, FileSerializer):
    class Meta:
        model = Document
        fields = ('id', 'created', 'updated', 'name', 'type', 'file_size', 'file_name', 'file_url')


class AddDocumentSerializer(DefaultSerializer):
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class ChangeDocumentSerializer(DefaultSerializer):
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)


class DocumentationPartSerializer(serializers.ModelSerializer, FileSerializer):
    class Meta:
        model = DocumentationPart
        fields = ('id', 'created', 'updated', 'name', 'order', 'file_size', 'file_name', 'file_url')


class AddDocumentationPartSerializer(DefaultSerializer):
    name = serializers.CharField(required=True)
    order = serializers.IntegerField(required=True)


class ChangeDocumentationPartSerializer(DefaultSerializer):
    name = serializers.CharField(required=False)
    order = serializers.IntegerField(required=False)


class SupplyContractSerializer(serializers.ModelSerializer, FileSerializer):
    class Meta:
        model = SupplyContract
        fields = ('id', 'created', 'updated', 'name',
                  'number', 'type', 'notes', 'start_date',
                  'expiration_date', 'file_size', 'file_name', 'file_url')


class AddSupplyContractSerializer(DefaultSerializer):
    name = serializers.CharField(required=True)
    number = serializers.IntegerField(required=False)
    type = serializers.CharField(required=True)
    notes = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    expiration_date = serializers.DateTimeField(required=False)


class ChangeSupplyContractSerializer(DefaultSerializer):
    name = serializers.CharField(required=False)
    number = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    expiration_date = serializers.DateTimeField(required=False)
