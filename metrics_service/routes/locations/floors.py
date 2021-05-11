from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.location import Floor, FloorPlanItem, FloorItemType, Room
from models.metrics import Meter
from permissions import is_admin_permission
from request_models.location_requests import FloorModel, AddFloorModel, ChangeFloorModel, AddFloorPlanItemModel, \
    FloorPlanItemModel
from routes import metrics_router


@metrics_router.get("/floors/", status_code=200, response_model=List[FloorModel])
async def get_floors(building_id: int = 0, db: Session = Depends(get_db)):
    floors = db.query(Floor)
    if building_id:
        floors = floors.filter_by(building_id=building_id)
    return [FloorModel.from_orm(b) for b in floors]


@metrics_router.get("/floors/{floor_id}/", status_code=200, response_model=FloorModel)
async def get_floor(floor_id: int = 0, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter_by(id=floor_id).first()
    if not floor:
        raise HTTPException(detail='Floor does not exist', status_code=404)

    return FloorModel.from_orm(floor)


@metrics_router.post("/floors/", status_code=201, response_model=FloorModel)
async def add_floor(body: AddFloorModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    floor = Floor(**body.dict())
    db.add(floor)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Floor already exists', status_code=400)
    return FloorModel.from_orm(floor)


@metrics_router.patch("/floors/{floor_id}", status_code=200, response_model=FloorModel)
async def patch_floor(floor_id: int, body: ChangeFloorModel, db: Session = Depends(get_db),
                      _=Depends(is_admin_permission)):
    floor = db.query(Floor).filter_by(id=floor_id).first()
    if not floor:
        raise HTTPException(detail='Floor does not exist', status_code=404)

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(floor, k, v)

        db.add(floor)
        db.commit()
    return FloorModel.from_orm(floor)


@metrics_router.delete("/floors/{floor_id}/", status_code=200)
async def remove_floor(floor_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(Floor).filter_by(id=floor_id).delete()
    db.commit()
    return ""


@metrics_router.post("/floor_plan_item-plan-items/", status_code=201, response_model=FloorPlanItemModel)
async def add_floor_plan_item(body: AddFloorPlanItemModel, db: Session = Depends(get_db),
                              _=Depends(is_admin_permission)):
    if not (floor := db.query(Floor).filter_by(id=body.floor_id).first()):
        raise HTTPException(detail='Floor does not exist', status_code=404)

    if body.type == FloorItemType.Meter:
        if not db.query(Meter).filter(Meter.id == body.item_id,
                                      or_(Meter.building_id == floor.building_id, Meter.building_id.is_(None))).first():
            raise HTTPException(detail='Meter does not exist', status_code=404)
    elif body.type == FloorItemType.Room and not db.query(Room).filter_by(id=body.item_id,
                                                                          floor_id=body.floor_id).first():
        raise HTTPException(detail='Room does not exist', status_code=404)
    floor_plan_item = FloorPlanItem(**body.dict())
    db.add(floor_plan_item)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='FloorPlanItem already exists', status_code=400)
    return FloorPlanItemModel.from_orm(floor_plan_item)


@metrics_router.delete("/floor_plan_item-plan-items/{floor_plan_item_id}/", status_code=200)
async def remove_floor_plan_item(floor_plan_item_id: int, db: Session = Depends(get_db),
                                 _=Depends(is_admin_permission)):
    db.query(FloorPlanItem).filter_by(id=floor_plan_item_id).delete()
    db.commit()
    return ""
