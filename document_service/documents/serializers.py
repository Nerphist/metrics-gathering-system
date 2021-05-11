from hurry.filesize import size
from rest_framework import serializers

from documents.models import Document, DocumentationPart, SupplyContract, Tariff, DocumentType
from utils import DefaultSerializer


class FileSerializer(DefaultSerializer):
    file_size = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    def get_file_size(self, obj):
        return size(obj.file.size) if obj.file else None

    def get_file_name(self, obj):
        return obj.file.name if obj.file else None

    def get_file_url(self, obj):
        return (self.context['request'].build_absolute_uri('/')[:-1] + '/media/' + str(obj.file)) if obj.file else None


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
        fields = ('id', 'created', 'updated', 'number', 'type', 'notes', 'start_date',
                  'expiration_date', 'file_size', 'file_name', 'file_url')


class AddSupplyContractSerializer(DefaultSerializer):
    number = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(required=True, choices=DocumentType.choices)
    notes = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    expiration_date = serializers.DateTimeField(required=False)


class ChangeSupplyContractSerializer(DefaultSerializer):
    number = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(required=False, choices=DocumentType.choices)
    notes = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    expiration_date = serializers.DateTimeField(required=False)


class TariffSerializer(serializers.ModelSerializer, FileSerializer):
    class Meta:
        model = Tariff
        fields = ('id', 'created', 'updated', 'type', 'notes', 'enacted_since',
                  'commercial_price', 'reduced_price', 'residential_price', 'file_size', 'file_name', 'file_url')


class AddTariffSerializer(DefaultSerializer):
    type = serializers.ChoiceField(required=True, choices=DocumentType.choices)
    notes = serializers.CharField(required=False)
    enacted_since = serializers.DateTimeField(required=False)
    commercial_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    reduced_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    residential_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)


class ChangeTariffSerializer(DefaultSerializer):
    type = serializers.ChoiceField(required=False, choices=DocumentType.choices)
    notes = serializers.CharField(required=False)
    enacted_since = serializers.DateTimeField(required=False)
    commercial_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    reduced_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    residential_price = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
