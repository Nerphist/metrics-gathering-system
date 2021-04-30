from datetime import datetime
from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.metrics import Device, Reading, DeviceType

ReadingModel = sqlalchemy_to_pydantic(Reading)


class RecognizeDeviceModel(BaseModel):
    device_exists: bool


class DeviceTypeModel(sqlalchemy_to_pydantic(DeviceType)):
    pass


class DeviceModel(sqlalchemy_to_pydantic(Device)):
    readings: List[ReadingModel]
    device_type: DeviceTypeModel


class AddReadingModel(BaseModel):
    value: str
    type: str
    date: datetime = datetime.utcnow()


class AddDeviceTypeModel(BaseModel):
    name: str


class AddDeviceModel(BaseModel):
    name: str
    device_type_id: int
    serial: str
    room_id: int = None
    model_number: str = ''
    description: str = ''
    manufacture_date: datetime = datetime.utcnow()


class ChangeDeviceModel(BaseModel):
    name: str = None
    device_type_id: int = None
    serial: str = None
    room_id: int = None
    model_number: str = None
    description: str = None
    manufacture_date: datetime = None
