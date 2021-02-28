from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import Reading, Device
from request_models.metrics import ReadingModel, AddReadingModel, DeviceModel, AddDeviceModel
from routes import metrics_router


@metrics_router.get("/readings/", status_code=200, response_model=List[ReadingModel])
async def get_readings(device_id: int = 0, db: Session = Depends(get_db)):
    readings = db.query(Reading)
    if device_id:
        readings = readings.filter_by(device_id=device_id)
    return [ReadingModel.from_orm(r) for r in readings]


@metrics_router.post("/readings/", status_code=201, response_model=ReadingModel)
async def add_reading(body: AddReadingModel, db: Session = Depends(get_db)):
    reading = Reading(date=body.date, type=body.type, value=body.value, device_id=body.device_id)
    db.add(reading)
    db.commit()
    return ReadingModel.from_orm(reading)


@metrics_router.get("/devices/", status_code=200, response_model=List[DeviceModel])
async def get_devices(room_id: int = 0, db: Session = Depends(get_db)):
    devices = db.query(Device)
    if room_id:
        devices = devices.filter_by(room_id=room_id)
    return [DeviceModel.from_orm(d) for d in devices]


@metrics_router.post("/devices/", status_code=201, response_model=DeviceModel)
async def add_device(body: AddDeviceModel, db: Session = Depends(get_db)):
    device = Device(type=body.type, room_id=body.room_id, name=body.name, serial=body.serial,
                    model_number=body.model_number, description=body.description,
                    manufacture_date=body.manufacture_date)
    db.add(device)
    db.commit()
    return DeviceModel.from_orm(device)


@metrics_router.delete("/devices/{device_id}/", status_code=200)
async def remove_device(device_id: int, db: Session = Depends(get_db)):
    db.query(Device).filter_by(id=device_id).delete()
    db.commit()
    return ""
