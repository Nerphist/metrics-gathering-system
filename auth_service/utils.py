from django.db import models
from rest_framework import serializers


class DefaultSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        super(self.__class__, self).update(instance, validated_data)

    def create(self, validated_data):
        super(self.__class__, self).create(validated_data)


class AbstractCreateUpdateModel(models.Model):
    class Meta:
        abstract = True
        ordering = ['pk']

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

