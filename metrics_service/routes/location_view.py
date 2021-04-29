from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_api import get_user
from db import get_db
from models.location import Building, Location, Floor, Room, ResponsibleUser
from permissions import is_admin_permission
from request_models.location_requests import BuildingModel, AddBuildingModel, FloorModel, AddFloorModel, RoomModel, \
    AddRoomModel, LocationModel, AddLocationModel, ResponsibleUserModel, AddResponsibleUserModel, ChangeRoomModel, \
    ChangeFloorModel, ChangeResponsibleUserModel, ChangeBuildingModel, ChangeLocationModel
from routes import metrics_router


@metrics_router.get("/structure/", status_code=200)
async def get_full_structure(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return {
        building.id: {
            floor.id: {
                room.id: [device.id for device in room.devices]
                for room in floor.rooms}
            for floor in building.floors}
        for building in buildings}


@metrics_router.get("/locations/", status_code=200, response_model=List[LocationModel])
async def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return [LocationModel.from_orm(b) for b in locations]


@metrics_router.post("/locations/", status_code=201, response_model=LocationModel)
async def add_location(body: AddLocationModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    location = Location(name=body.name, latitude=body.latitude, longitude=body.longitude)
    db.add(location)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Location already exists', status_code=400)
    return LocationModel.from_orm(location)


@metrics_router.patch("/locations/{location_id}", status_code=200, response_model=LocationModel)
async def patch_location(location_id: int, body: ChangeLocationModel, db: Session = Depends(get_db),
                         _=Depends(is_admin_permission)):
    location = db.query(Location).filter_by(id=location_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(location, k, v)

        db.add(location)
        db.commit()
    return LocationModel.from_orm(location)


@metrics_router.delete("/locations/{location_id}/", status_code=200)
async def remove_location(location_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(Location).filter_by(id=location_id).delete()
    db.commit()
    return ""


@metrics_router.get("/buildings/", status_code=200, response_model=List[BuildingModel])
async def get_buildings(db: Session = Depends(get_db)):
    building_models = db.query(Building).all()
    buildings = [BuildingModel.from_orm(b) for b in building_models]
    for index, building in enumerate(building_models):
        for user in building.responsible_users:
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

    args = {k: v for k, v in body.dict().items() if v}
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


@metrics_router.get("/responsible_users/", status_code=200, response_model=List[ResponsibleUserModel])
async def get_responsible_users(db: Session = Depends(get_db)):
    responsible_user_models = db.query(ResponsibleUser).all()

    return [{'id': user.id, 'name': user.name, 'user': get_user(user.user_id)} for user in responsible_user_models]


@metrics_router.post("/responsible_users/", status_code=201, response_model=ResponsibleUserModel)
async def add_responsible_user(body: AddResponsibleUserModel, db: Session = Depends(get_db),
                               _=Depends(is_admin_permission)):
    if not (user := get_user(body.user_id)):
        raise HTTPException(detail='User does not exist', status_code=400)
    responsible_user = ResponsibleUser(**body.dict())
    db.add(responsible_user)
    db.commit()
    return {'id': responsible_user.id, 'name': responsible_user.name, 'user': user}


@metrics_router.patch("/responsible_users/{responsible_user_id}", status_code=200, response_model=ResponsibleUserModel)
async def patch_responsible_user(responsible_user_id: int, body: ChangeResponsibleUserModel,
                                 db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    responsible_user = db.query(ResponsibleUser).filter_by(id=responsible_user_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(responsible_user, k, v)

        db.add(responsible_user)
        db.commit()
    return ResponsibleUserModel.from_orm(responsible_user)


@metrics_router.delete("/responsible_users/{responsible_user_id}/", status_code=200)
async def remove_responsible_user(responsible_user_id: int, db: Session = Depends(get_db),
                                  _=Depends(is_admin_permission)):
    db.query(ResponsibleUser).filter_by(id=responsible_user_id).delete()
    db.commit()
    return ""


@metrics_router.delete("/responsible_users/users/{user_id}/", status_code=200)
async def remove_responsible_user_by_user_id(user_id: int, db: Session = Depends(get_db),
                                             _=Depends(is_admin_permission)):
    db.query(ResponsibleUser).filter_by(user_id=user_id).delete()
    db.commit()
    return ""


@metrics_router.get("/floors/", status_code=200, response_model=List[FloorModel])
async def get_floors(building_id: int = 0, db: Session = Depends(get_db)):
    floors = db.query(Floor)
    if building_id:
        floors = floors.filter_by(building_id=building_id)
    return [FloorModel.from_orm(b) for b in floors.all()]


@metrics_router.post("/floors/", status_code=201, response_model=FloorModel)
async def add_floor(body: AddFloorModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    floor = Floor(building_id=body.building_id, number=body.number)
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

    args = {k: v for k, v in body.dict().items() if v}
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


@metrics_router.get("/rooms/", status_code=200, response_model=List[RoomModel])
async def get_rooms(floor_id: int = 0, db: Session = Depends(get_db)):
    rooms = db.query(Floor)
    if floor_id:
        rooms = rooms.filter_by(floor_id=floor_id)
    return [RoomModel.from_orm(b) for b in rooms]


@metrics_router.post("/rooms/", status_code=201, response_model=RoomModel)
async def add_room(body: AddRoomModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    room = Room(floor_id=body.floor_id, name=body.name)
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

    args = {k: v for k, v in body.dict().items() if v}
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
