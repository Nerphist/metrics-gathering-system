from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_api import get_user
from db import get_db
from models.location import Building, BuildingType
from permissions import is_admin_permission
from request_models.location_requests import BuildingModel, AddBuildingModel, ChangeBuildingModel, BuildingTypeModel, \
    AddBuildingTypeModel, BuildingTypeCountModel
from routes import metrics_router


@metrics_router.get("/building_types/", status_code=200, response_model=List[BuildingTypeModel])
async def get_building_types(db: Session = Depends(get_db)):
    building_types = db.query(BuildingType).all()
    return [BuildingTypeModel.from_orm(b) for b in building_types]


@metrics_router.get("/building_types/count/", status_code=200, response_model=List[BuildingTypeCountModel])
async def get_building_types(db: Session = Depends(get_db)):
    building_types = db.query(BuildingType).all()
    return [BuildingTypeCountModel(id=b.id, name=b.name, buildings_count=len(b.buildings)) for b in building_types]


@metrics_router.post("/building_types/", status_code=201, response_model=BuildingTypeModel)
async def add_building_type(body: AddBuildingTypeModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    building_type = BuildingType(name=body.name)
    db.add(building_type)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='BuildingType already exists', status_code=400)
    return BuildingTypeModel.from_orm(building_type)


@metrics_router.patch("/building_types/{building_type_id}", status_code=200, response_model=BuildingTypeModel)
async def patch_building_type(building_type_id: int, body: AddBuildingTypeModel, db: Session = Depends(get_db),
                              _=Depends(is_admin_permission)):
    building_type = db.query(BuildingType).filter_by(id=building_type_id).first()

    building_type.name = body.name
    db.add(building_type)
    db.commit()
    return BuildingTypeModel.from_orm(building_type)


@metrics_router.delete("/building_types/{building_type_id}/", status_code=200)
async def remove_building_type(building_type_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(BuildingType).filter_by(id=building_type_id).delete()
    db.commit()
    return ""


@metrics_router.get("/buildings/", status_code=200, response_model=List[BuildingModel])
async def get_buildings(db: Session = Depends(get_db), building_type_id: int = 0, location_id: int = 0, ):
    building_models = db.query(Building)
    if building_type_id:
        building_models = building_models.filter_by(building_type_id=building_type_id)
    if location_id:
        building_models = building_models.filter_by(location_id=location_id)
    building_models = building_models.all()

    buildings = [BuildingModel.from_orm(b) for b in building_models]
    for index, building in enumerate(building_models):
        for user in building.responsible_people:
            user.user = get_user(user.user_id)
    return buildings


@metrics_router.post("/buildings/", status_code=201, response_model=BuildingModel)
async def add_building(body: AddBuildingModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    building = Building(**body.dict())
    db.add(building)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Building already exists', status_code=400)
    return BuildingModel.from_orm(building)


@metrics_router.patch("/buildings/{building_id}", status_code=200, response_model=BuildingModel)
async def patch_building(building_id: int, body: ChangeBuildingModel,
                         db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    building = db.query(Building).filter_by(id=building_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(building, k, v)

        db.add(building)
        db.commit()
    return BuildingModel.from_orm(building)


@metrics_router.delete("/buildings/{building_id}/", status_code=200)
async def remove_building(building_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(Building).filter_by(id=building_id).delete()
    db.commit()
    return ""

