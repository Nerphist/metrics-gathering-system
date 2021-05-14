from typing import Type, List

from django.db import models
from django.db.models.sql import Query
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response

from users.utils import is_admin_of_parent_group


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


def make_pagination_serializer(serializer: Type['serializers.Serializer']):
    class PaginationSerializer(DefaultSerializer):
        total_size = serializers.IntegerField(required=True)
        page_number = serializers.IntegerField(required=True)
        page_size = serializers.IntegerField(required=True)
        items = serializer(many=True)

    return type(f'Pagination{serializer.__name__}', (PaginationSerializer,), dict(PaginationSerializer.__dict__))()


def paginate(db_model: Type['models.Model'], serializer: Type['serializers.Serializer'], request: Request,
             query: Query = None, query_params: dict = None):
    if not query:
        query = db_model.objects

    if query_params is None:
        query_params = {k: v[0] for k, v in dict(request.query_params).items()}

    for key, val in query_params.items():
        if key.endswith('__in') or key == 'order_by':
            query_params[key] = [s.strip() for s in val.split(',')]

    page_number = int(query_params.pop('page_number', 1))
    page_size = int(query_params.pop('page_size', 10))

    order_by = query_params.pop('order_by', [])

    query = query.filter(**query_params)

    query = query.order_by(*order_by)

    count = query.count()

    result_models = query[(page_number - 1) * page_size: page_number * page_size]
    items = [serializer(obj, context={'request': request}).data for obj in result_models]
    return Response(data={
        'total_size': count,
        'page_number': page_number,
        'page_size': len(items),
        'items': items
    })


def check_if_user_has_permission(user, permission_names: List[str]):
    permission_set = set()
    groups = user.user_groups
    for user_group in groups.all():
        permission_set.update(user_group.permissions)
    return set(permission_names).issubset(permission_set)
