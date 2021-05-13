from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_api import get_user
from db import get_db
from models import PermissionSet
from models.location import Building, BuildingType
from permissions import has_permission
from request_models import create_pagination_model
from request_models.location_requests import BuildingModel, AddBuildingModel, ChangeBuildingModel, BuildingTypeModel, \
    AddBuildingTypeModel, BuildingTypeCountModel
from routes import metrics_router
from utils import paginate, apply_filtering


@metrics_router.get("/building-types/", status_code=200, response_model=create_pagination_model(BuildingTypeModel))
async def get_building_types(request: Request, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.BuildingTypeRead.value)
    return paginate(
        db=db,
        db_model=BuildingType,
        serializer=BuildingTypeModel,
        request=request
    )


@metrics_router.get("/building-types/count/", status_code=200,
                    response_model=create_pagination_model(BuildingTypeCountModel))
async def get_building_types_count(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingTypeRead.value)
    result_models, count, page_number = apply_filtering(db, BuildingType, request)
    items = [BuildingTypeCountModel(id=b.id, name=b.name, buildings_count=len(b.buildings)) for b in result_models]
    return {
        'total_size': count,
        'page_number': page_number,
        'page_size': len(items),
        'items': items
    }


@metrics_router.post("/building-types/", status_code=201, response_model=BuildingTypeModel)
async def add_building_type(request: Request, body: AddBuildingTypeModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingTypeEdit.value)
    building_type = BuildingType(name=body.name)
    db.add(building_type)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='BuildingType already exists', status_code=400)
    return BuildingTypeModel.from_orm(building_type)


@metrics_router.patch("/building-types/{building_type_id}", status_code=200, response_model=BuildingTypeModel)
async def patch_building_type(request: Request, building_type_id: int, body: AddBuildingTypeModel,
                              db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.BuildingTypeEdit.value)
    building_type = db.query(BuildingType).filter_by(id=building_type_id).first()

    building_type.name = body.name
    db.add(building_type)
    db.commit()
    return BuildingTypeModel.from_orm(building_type)


@metrics_router.delete("/building-types/{building_type_id}/", status_code=200)
async def remove_building_type(request: Request, building_type_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingTypeEdit.value)
    db.query(BuildingType).filter_by(id=building_type_id).delete()
    db.commit()
    return ""


@metrics_router.get("/buildings/", status_code=200, response_model=create_pagination_model(BuildingModel))
async def get_buildings(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingRead.value)
    paginated = paginate(
        db=db,
        db_model=Building,
        serializer=BuildingModel,
        request=request
    )
    for index, building in enumerate(paginated['items']):
        for user in building.responsible_people:
            user.user = get_user(user.user_id)
    return paginated


@metrics_router.post("/buildings/", status_code=201, response_model=BuildingModel)
async def add_building(request: Request, body: AddBuildingModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingEdit.value)
    building = Building(**body.dict())
    db.add(building)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Building already exists', status_code=400)
    return BuildingModel.from_orm(building)


@metrics_router.patch("/buildings/{building_id}", status_code=200, response_model=BuildingModel)
async def patch_building(request: Request, building_id: int, body: ChangeBuildingModel,
                         db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingEdit.value)
    building = db.query(Building).filter_by(id=building_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(building, k, v)

        db.add(building)
        db.commit()
    return BuildingModel.from_orm(building)


@metrics_router.delete("/buildings/{building_id}/", status_code=200)
async def remove_building(request: Request, building_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingEdit.value)
    db.query(Building).filter_by(id=building_id).delete()
    db.commit()
    return ""
