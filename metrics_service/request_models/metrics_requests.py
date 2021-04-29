from datetime import datetime
from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.metrics import Device, Reading

ReadingModel = sqlalchemy_to_pydantic(Reading)


class RecognizeDeviceModel(BaseModel):
    device_exists: bool


class DeviceModel(sqlalchemy_to_pydantic(Device)):
    readings: List[ReadingModel]


class AddReadingModel(BaseModel):
    value: str
    type: str
    date: datetime = datetime.utcnow()


class AddDeviceModel(BaseModel):
    name: str
    type: str
    serial: str
    room_id: int = None
    model_number: str = ''
    description: str = ''
    manufacture_date: datetime = datetime.utcnow()


class ChangeDeviceModel(BaseModel):
    name: str = None
    type: str = None
    serial: str = None
    room_id: int = None
    model_number: str = None
    description: str = None
    manufacture_date: datetime = None
