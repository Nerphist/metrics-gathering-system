from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import login_rule, user_eligible_for_login, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken
from hurry.filesize import size

from documents.models import Document
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
