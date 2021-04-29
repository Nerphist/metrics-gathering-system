from typing import List, Any

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.location import Location, Building, Floor, Room
from request_models.metrics_requests import DeviceModel


class ContactInfoModel(BaseModel):
    id: int
    name: str
    value: str
    type: str
    notes: str


class UserModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_admin: bool
    contact_infos: List[ContactInfoModel]


class ResponsibleUserModel(BaseModel):
    id: int
    name: str
    user: UserModel


class RoomModel(sqlalchemy_to_pydantic(Room)):
    devices: List[DeviceModel]


class FloorModel(sqlalchemy_to_pydantic(Floor)):
    rooms: List[RoomModel]


class BuildingModel(sqlalchemy_to_pydantic(Building)):
    floors: List[FloorModel]
    responsible_users: Any


class LocationModel(sqlalchemy_to_pydantic(Location)):
    buildings: List[BuildingModel]


class AddLocationModel(BaseModel):
    name: str
    latitude: int
    longitude: int


class AddBuildingModel(BaseModel):
    location_id: int
    name: str

    description: str = None
    address: str = None
    building_index: str = None
    building_type: str = None

    last_capital_repair_year: int = None
    construction_year: int = None


class AddResponsibleUserModel(BaseModel):
    user_id: int
    building_id: int
    name: str


class AddFloorModel(BaseModel):
    building_id: int
    number: int


class AddRoomModel(BaseModel):
    floor_id: int
    name: str
