from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.location import Floor
from permissions import is_admin_permission
from request_models.location_requests import FloorModel, AddFloorModel, ChangeFloorModel
from routes import metrics_router


@metrics_router.get("/floors/", status_code=200, response_model=List[FloorModel])
async def get_floors(building_id: int = 0, db: Session = Depends(get_db)):
    floors = db.query(Floor)
    if building_id:
        floors = floors.filter_by(building_id=building_id)
    return [FloorModel.from_orm(b) for b in floors]


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