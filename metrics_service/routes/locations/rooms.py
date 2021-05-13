from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.location import Room
from permissions import has_permission
from request_models import create_pagination_model
from request_models.location_requests import RoomModel, \
    AddRoomModel, ChangeRoomModel
from routes import metrics_router
from utils import paginate


@metrics_router.get("/rooms/", status_code=200, response_model=create_pagination_model(RoomModel))
async def get_rooms(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.RoomRead.value)
    return paginate(
        db=db,
        db_model=Room,
        serializer=RoomModel,
        request=request
    )


@metrics_router.post("/rooms/", status_code=201, response_model=RoomModel)
async def add_room(request: Request, body: AddRoomModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.RoomEdit.value)
    room = Room(**body.dict())
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Room already exists', status_code=400)
    return RoomModel.from_orm(room)


@metrics_router.patch("/rooms/{room_id}", status_code=200, response_model=RoomModel)
async def patch_room(request: Request, room_id: int, body: ChangeRoomModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.RoomEdit.value)
    room = db.query(Room).filter_by(id=room_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(room, k, v)

        db.add(room)
        db.commit()
    return RoomModel.from_orm(room)


@metrics_router.delete("/rooms/{room_id}/", status_code=200)
async def remove_room(request: Request, room_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.RoomEdit.value)
    db.query(Room).filter_by(id=room_id).delete()
    db.commit()
    return ""
