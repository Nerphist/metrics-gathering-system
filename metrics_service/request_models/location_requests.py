from typing import List, Any

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.location import Location, Building, Room, BuildingType, Floor, ResponsibleUser, FloorPlanItem
from request_models import make_change_model, make_add_model
from request_models.metrics_requests import MeterModel


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
    contact_infos: List[ContactInfoModel]
    permissions: List[str]


class ResponsibleUserModel(BaseModel):
    id: int
    rank: str
    building_id: int
    user: UserModel


class RoomModel(sqlalchemy_to_pydantic(Room)):
    pass


class FloorPlanItemModel(sqlalchemy_to_pydantic(FloorPlanItem)):
    pass


class FloorModel(sqlalchemy_to_pydantic(Floor)):
    rooms: List[RoomModel]
    items: List[FloorPlanItemModel]


class BuildingTypeCountModel(BaseModel):
    id: int
    name: str
    buildings_count: int


class BuildingModel(sqlalchemy_to_pydantic(Building)):
    floors: List[FloorModel]
    meters: List[MeterModel]
    building_type: sqlalchemy_to_pydantic(BuildingType)
    location: sqlalchemy_to_pydantic(Location)
    responsible_people: Any


class LocationModel(sqlalchemy_to_pydantic(Location)):
    buildings: List[BuildingModel]


class BuildingTypeModel(sqlalchemy_to_pydantic(BuildingType)):
    pass


AddResponsibleUserModel = make_add_model(sqlalchemy_to_pydantic(ResponsibleUser))
AddLocationModel = make_add_model(sqlalchemy_to_pydantic(Location))
AddBuildingTypeModel = make_add_model(sqlalchemy_to_pydantic(BuildingType))
AddBuildingModel = make_add_model(sqlalchemy_to_pydantic(Building))
AddFloorModel = make_add_model(sqlalchemy_to_pydantic(Floor))
AddFloorPlanItemModel = make_add_model(sqlalchemy_to_pydantic(FloorPlanItem))
AddRoomModel = make_add_model(sqlalchemy_to_pydantic(Room))

ChangeResponsibleUserModel = make_change_model(sqlalchemy_to_pydantic(ResponsibleUser))
ChangeLocationModel = make_change_model(sqlalchemy_to_pydantic(Location))
ChangeBuildingTypeModel = make_change_model(sqlalchemy_to_pydantic(BuildingType))
ChangeBuildingModel = make_change_model(sqlalchemy_to_pydantic(Building))
ChangeFloorModel = make_change_model(sqlalchemy_to_pydantic(Floor))
ChangeRoomModel = make_change_model(sqlalchemy_to_pydantic(Room))
