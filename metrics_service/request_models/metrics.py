from datetime import datetime
from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.metrics import Device, Reading

ReadingModel = sqlalchemy_to_pydantic(Reading)


class DeviceModel(sqlalchemy_to_pydantic(Device)):
    readings: List[ReadingModel]


class AddReadingModel(BaseModel):
    value: str
    type: str
    device_id: int
    date: datetime = datetime.utcnow()


class AddDeviceModel(BaseModel):
    name: str
    type: str
    serial: str
    room_id: int = None
    model_number: str = ''
    description: str = ''
    manufacture_date: datetime = datetime.utcnow()
