from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.location import Room
from permissions import is_admin_permission
from request_models.location_requests import RoomModel, \
    AddRoomModel, ChangeRoomModel
from routes import metrics_router


@metrics_router.get("/rooms/", status_code=200, response_model=List[RoomModel])
async def get_rooms(floor_id: int = 0, db: Session = Depends(get_db)):
    rooms = db.query(Room)
    if floor_id:
        rooms = rooms.filter_by(floor_id=floor_id)
    return [RoomModel.from_orm(b) for b in rooms]


@metrics_router.post("/rooms/", status_code=201, response_model=RoomModel)
async def add_room(body: AddRoomModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    room = Room(**body.dict())
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Room already exists', status_code=400)
    return RoomModel.from_orm(room)


@metrics_router.patch("/rooms/{room_id}", status_code=200, response_model=RoomModel)
async def patch_room(room_id: int, body: ChangeRoomModel, db: Session = Depends(get_db),
                     _=Depends(is_admin_permission)):
    room = db.query(Room).filter_by(id=room_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(room, k, v)

        db.add(room)
        db.commit()
    return RoomModel.from_orm(room)


@metrics_router.delete("/rooms/{room_id}/", status_code=200)
async def remove_room(room_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(Room).filter_by(id=room_id).delete()
    db.commit()
    return ""