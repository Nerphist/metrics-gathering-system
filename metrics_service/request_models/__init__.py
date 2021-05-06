from pydantic.main import BaseModel


def make_change_model(model: BaseModel) -> BaseModel:
    model.__fields__.pop('id')
    for field in model.__fields__.values():
        if field.default == Ellipsis:
            field.default = None
        field.required = False
    return type(f'Change{model.__name__}Model', (BaseModel,), dict(model.__dict__))


def make_add_model(model: BaseModel) -> BaseModel:
    model.__fields__.pop('id')
    return type(f'Add{model.__name__}Model', (BaseModel,), dict(model.__dict__))
