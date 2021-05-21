from typing import Type

from fastapi import Request
from pydantic.main import BaseModel
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from db import Base


def apply_filtering(db: Session, db_model: Type['Base'], request: Request):
    query = db.query(db_model)

    query_params = dict(request.query_params)
    page_number = int(query_params.pop('page_number', 1))
    page_size = int(query_params.pop('page_size', 10))

    order_by = query_params.pop('order_by', None)
    order_by = [s.strip() for s in order_by.split(',')] if order_by else []
    for filter_arg, value in query_params.items():
        filter_arg = filter_arg.split('__')
        if len(filter_arg) > 1:
            operator = filter_arg[1]
        else:
            operator = 'eq'
        filter_arg = filter_arg[0]
        if operator == 'gt':
            query = query.filter(getattr(db_model, filter_arg) > value)
        if operator == 'gte':
            query = query.filter(getattr(db_model, filter_arg) >= value)
        if operator == 'lt':
            query = query.filter(getattr(db_model, filter_arg) < value)
        if operator == 'lte':
            query = query.filter(getattr(db_model, filter_arg) <= value)
        if operator == 'eq':
            query = query.filter(getattr(db_model, filter_arg) == value)
        if operator == 'neq':
            query = query.filter(getattr(db_model, filter_arg) != value)
        if operator == 'icontains':
            query = query.filter(getattr(db_model, filter_arg).ilike(f'%{value}%'))
        if operator == 'in':
            value = [s.strip() for s in value.split(',')]
            query = query.filter(getattr(db_model, filter_arg).in_(value))

    ordering_params = []
    for ordering in order_by:
        sign = ordering[0]
        if sign == '-':
            ordering_params.append(desc(getattr(db_model, ordering[1:])))
        else:
            ordering_params.append(asc(getattr(db_model, ordering)))

    query = query.order_by(*ordering_params)
    count = query.count()
    query = query.limit(page_size).offset((page_number - 1) * page_size)

    result_models = query.all()

    return result_models, count, page_number


def paginate(db: Session, db_model: Type['Base'], serializer: Type['BaseModel'], request: Request):
    result_models, count, page_number = apply_filtering(db, db_model, request)

    items = [serializer.from_orm(obj) for obj in result_models]
    return {
        'total_size': count,
        'page_number': page_number,
        'page_size': len(items),
        'items': items
    }
