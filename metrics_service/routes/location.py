from typing import List

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db import get_db
from models.location import Building, Location, Floor, Room
from request_models.location import BuildingModel, AddBuildingModel, FloorModel, AddFloorModel, RoomModel, AddRoomModel
from routes import metrics_router


@metrics_router.get("/buildings/", status_code=200, response_model=List[BuildingModel])
async def get_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return [BuildingModel.from_orm(b) for b in buildings]


@metrics_router.post("/buildings/", status_code=201, response_model=BuildingModel)
async def add_building(body: AddBuildingModel, db: Session = Depends(get_db)):
    location = Location(name=body.name, latitude=body.latitude, longitude=body.longitude)
    building = Building()
    building.location = location
    db.add(building)
    try:
        db.commit()
    except IntegrityError:
        return JSONResponse(content={'detail': 'Building already exists'}, status_code=400)
    return BuildingModel.from_orm(building)


@metrics_router.delete("/buildings/{building_id}/", status_code=200)
async def remove_building(building_id: int, db: Session = Depends(get_db)):
    db.query(Building).filter_by(id=building_id).delete()
    db.commit()
    return ""


@metrics_router.get("/floors/", status_code=200, response_model=List[FloorModel])
async def get_floors(building_id: int = 0, db: Session = Depends(get_db)):
    floors = db.query(Floor)
    if building_id:
        floors = floors.filter_by(building_id=building_id)
    return [FloorModel.from_orm(b) for b in floors.all()]


@metrics_router.post("/floors/", status_code=201, response_model=FloorModel)
async def add_floor(body: AddFloorModel, db: Session = Depends(get_db)):
    floor = Floor(building_id=body.building_id, number=body.number)
    db.add(floor)
    try:
        db.commit()
    except IntegrityError:
        return JSONResponse(content={'detail': 'Floor already exists'}, status_code=400)
    return FloorModel.from_orm(floor)


@metrics_router.delete("/floors/{floor_id}/", status_code=200)
async def remove_floor(floor_id: int, db: Session = Depends(get_db)):
    db.query(Floor).filter_by(id=floor_id).delete()
    db.commit()
    return ""


@metrics_router.get("/rooms/", status_code=200, response_model=List[RoomModel])
async def get_rooms(floor_id: int = 0, db: Session = Depends(get_db)):
    rooms = db.query(Floor)
    if floor_id:
        rooms = rooms.filter_by(floor_id=floor_id)
    return [RoomModel.from_orm(b) for b in rooms]


@metrics_router.post("/rooms/", status_code=201, response_model=RoomModel)
async def add_room(body: AddRoomModel, db: Session = Depends(get_db)):
    room = Room(floor_id=body.floor_id, name=body.name)
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        return JSONResponse(content={'detail': 'Room already exists'}, status_code=400)
    return RoomModel.from_orm(room)


@metrics_router.delete("/rooms/{room_id}/", status_code=200)
async def remove_room(room_id: int, db: Session = Depends(get_db)):
    db.query(Room).filter_by(id=room_id).delete()
    db.commit()
    return ""

@metrics_router.delete("/rooms/{room_id}/", status_code=200)
async def remove_room(room_id: int, db: Session = Depends(get_db)):
    db.query(Room).filter_by(id=room_id).delete()
    db.commit()
    return ""
