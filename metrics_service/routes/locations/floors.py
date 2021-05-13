from fastapi import Depends, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.location import Floor, FloorPlanItem, FloorItemType, Room
from models.metrics import Meter
from permissions import has_permission
from request_models import create_pagination_model
from request_models.location_requests import FloorModel, AddFloorModel, ChangeFloorModel, AddFloorPlanItemModel, \
    FloorPlanItemModel
from routes import metrics_router
from utils import paginate


@metrics_router.get("/floors/", status_code=200, response_model=create_pagination_model(FloorModel))
async def get_floors(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.FloorRead.value)
    return paginate(
        db=db,
        db_model=Floor,
        serializer=FloorModel,
        request=request
    )


@metrics_router.post("/floors/", status_code=201, response_model=FloorModel)
async def add_floor(request: Request, body: AddFloorModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.FloorEdit.value)
    floor = Floor(**body.dict())
    db.add(floor)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Floor already exists', status_code=400)
    return FloorModel.from_orm(floor)


@metrics_router.patch("/floors/{floor_id}", status_code=200, response_model=FloorModel)
async def patch_floor(request: Request, floor_id: int, body: ChangeFloorModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.FloorEdit.value)
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
async def remove_floor(request: Request, floor_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.FloorEdit.value)
    db.query(Floor).filter_by(id=floor_id).delete()
    db.commit()
    return ""


@metrics_router.post("/floor-plan-items/", status_code=201, response_model=FloorPlanItemModel)
async def add_floor_plan_item(request: Request, body: AddFloorPlanItemModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.FloorEdit.value)
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


@metrics_router.delete("/floor-plan-items/{floor_plan_item_id}/", status_code=200)
async def remove_floor_plan_item(request: Request, floor_plan_item_id: int, db: Session = Depends(get_db),
                                 ):
    has_permission(request, PermissionSet.FloorEdit.value)
    db.query(FloorPlanItem).filter_by(id=floor_plan_item_id).delete()
    db.commit()
    return ""
