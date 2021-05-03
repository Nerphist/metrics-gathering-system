from typing import List, Any

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.location import Location, Building, Room, BuildingType
from request_models.metrics_requests import DeviceModel


class HeadcountModel(BaseModel):
    personnel: int = 0
    living: int = 0
    studying: int = 0


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


class BuildingTypeCountModel(BaseModel):
    id: int
    name: str
    buildings_count: int


class BuildingModel(sqlalchemy_to_pydantic(Building)):
    rooms: List[RoomModel]
    building_type: sqlalchemy_to_pydantic(BuildingType)
    location: sqlalchemy_to_pydantic(Location)
    responsible_users: Any


class LocationModel(sqlalchemy_to_pydantic(Location)):
    buildings: List[BuildingModel]


class BuildingTypeModel(sqlalchemy_to_pydantic(BuildingType)):
    buildings: List[BuildingModel]


class AddLocationModel(BaseModel):
    name: str
    latitude: float
    longitude: float


class AddBuildingModel(BaseModel):
    location_id: int
    name: str

    description: str = None
    address: str = None
    building_index: str = None
    building_type_id: int = None

    last_capital_repair_year: int = None
    construction_year: int = None

    living_quantity: int = 0
    studying_daytime: int = 0
    studying_evening_time: int = 0
    studying_part_time: int = 0
    working_teachers: int = 0
    working_science: int = 0
    working_help: int = 0


class AddResponsibleUserModel(BaseModel):
    user_id: int
    building_id: int
    name: str


class AddRoomModel(BaseModel):
    building_id: int
    name: str
    size: float = None
    designation: str = None
    responsible_department: str = None


class AddBuildingTypeModel(BaseModel):
    name: str


class ChangeLocationModel(BaseModel):
    name: str = None
    latitude: float = None
    longitude: float = None


class ChangeBuildingModel(BaseModel):
    name: str = None
    description: str = None
    address: str = None
    building_index: str = None
    building_type_id: int = None
    last_capital_repair_year: int = None
    construction_year: int = None
    living_quantity: int = None
    studying_daytime: int = None
    studying_evening_time: int = None
    studying_part_time: int = None
    working_teachers: int = None
    working_science: int = None
    working_help: int = None


class ChangeResponsibleUserModel(BaseModel):
    building_id: int = None
    name: str = None


class ChangeRoomModel(BaseModel):
    name: str = None
    size: float = None
    designation: str = None
    responsible_department: str = None
