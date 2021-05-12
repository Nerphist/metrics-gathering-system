from typing import List, Type

from pydantic.main import BaseModel


def _remove_fields(model, fields_to_remove: List):
    model.__fields__.pop('id', None)
    model.__fields__.pop('snapshot_id', None)
    if fields_to_remove:
        for field in fields_to_remove:
            model.__fields__.pop(field, None)


def make_change_model(model: BaseModel, fields_to_remove: List[str] = None) -> BaseModel:
    _remove_fields(model, fields_to_remove)
    for field in model.__fields__.values():
        if field.default == Ellipsis:
            field.default = None
        field.required = False
    return type(f'Change{model.__name__}Model', (BaseModel,), dict(model.__dict__))


def make_add_model(model: BaseModel, fields_to_remove: List[str] = None) -> BaseModel:
    _remove_fields(model, fields_to_remove)
    return type(f'Add{model.__name__}Model', (BaseModel,), dict(model.__dict__))


def create_pagination_model(entity_type: Type['BaseModel']) -> BaseModel:
    class PaginationModel(BaseModel):
        total_size: int
        page_number: int
        page_size: int
        items: List[entity_type]

    return type(f'Paginate{entity_type.__name__}', (BaseModel,), dict(PaginationModel.__dict__))
