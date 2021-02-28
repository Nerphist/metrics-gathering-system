from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.location import Location, Building, Floor, Room

LocationModel = sqlalchemy_to_pydantic(Location)
RoomModel = sqlalchemy_to_pydantic(Room)


class FloorModel(sqlalchemy_to_pydantic(Floor)):
    rooms: List[RoomModel]


class BuildingModel(sqlalchemy_to_pydantic(Building)):
    location: LocationModel
    floors: List[FloorModel]


class AddBuildingModel(BaseModel):
    name: str
    latitude: int
    longitude: int


class AddFloorModel(BaseModel):
    building_id: int
    number: int


class AddRoomModel(BaseModel):
    floor_id: int
    name: str
