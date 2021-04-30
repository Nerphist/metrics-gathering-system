from typing import List, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import Reading, Device, DeviceType
from permissions import is_admin_permission
from request_models.metrics_requests import ReadingModel, AddReadingModel, DeviceModel, AddDeviceModel, \
    RecognizeDeviceModel, ChangeDeviceModel, DeviceTypeModel, AddDeviceTypeModel
from routes import metrics_router


@metrics_router.get("/readings/", status_code=200, response_model=List[ReadingModel])
async def get_readings(device_id: int = 0, db: Session = Depends(get_db)):
    readings = db.query(Reading)
    if device_id:
        readings = readings.filter_by(device_id=device_id)
    readings = readings.all()
    return [ReadingModel.from_orm(r) for r in readings]


@metrics_router.post("/readings/", status_code=201, response_model=ReadingModel)
async def add_reading(body: AddReadingModel, db: Session = Depends(get_db), secret_key: Optional[str] = Header(None)):
    reading = Reading(date=body.date, type=body.type, value=body.value)
    device = db.query(Device).filter(Device.secret_key == secret_key).first()
    if not device:
        raise HTTPException(status_code=400, detail="Wrong secret key")

    reading.device_id = device.id
    db.add(reading)
    db.commit()
    return ReadingModel.from_orm(reading)


@metrics_router.get("/devices/recognize/{recognition_key}/", status_code=201, response_model=RecognizeDeviceModel)
async def recognize_device(recognition_key: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.recognition_key == recognition_key).first()
    if not device:
        return {'device_exists': False}
    return {'device_exists': True}


@metrics_router.get("/devices/", status_code=200, response_model=List[DeviceModel])
async def get_devices(room_id: int = 0, device_name: str = '', db: Session = Depends(get_db)):
    devices = db.query(Device)
    if room_id:
        devices = devices.filter_by(room_id=room_id)
    if device_name:
        devices = devices.filter(Device.name.contains(device_name))
    devices = devices.all()
    return [DeviceModel.from_orm(d) for d in devices]


@metrics_router.post("/devices/", status_code=201, response_model=DeviceModel)
async def add_device(body: AddDeviceModel, db: Session = Depends(get_db)):
    device = Device(**body.dict())
    db.add(device)
    db.commit()
    return DeviceModel.from_orm(device)


@metrics_router.patch("/devices/{device_id}", status_code=200, response_model=DeviceModel)
async def patch_device(device_id: int, body: ChangeDeviceModel, db: Session = Depends(get_db),
                       _=Depends(is_admin_permission)):
    device = db.query(Device).filter_by(id=device_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(device, k, v)

        db.add(device)
        db.commit()
    return DeviceModel.from_orm(device)


@metrics_router.delete("/devices/{device_id}/", status_code=200)
async def remove_device(device_id: int, db: Session = Depends(get_db)):
    db.query(Device).filter_by(id=device_id).delete()
    db.commit()
    return ""


@metrics_router.get("/device_types/", status_code=200, response_model=List[DeviceTypeModel])
async def get_device_types(room_id: int = 0, device_type_name: str = '', db: Session = Depends(get_db)):
    device_types = db.query(DeviceType)
    if room_id:
        device_types = device_types.filter_by(room_id=room_id)
    if device_type_name:
        device_types = device_types.filter(DeviceType.name.contains(device_type_name))
    device_types = device_types.all()
    return [DeviceTypeModel.from_orm(d) for d in device_types]


@metrics_router.post("/device_types/", status_code=201, response_model=DeviceTypeModel)
async def add_device_type(body: AddDeviceTypeModel, db: Session = Depends(get_db)):
    device_type = DeviceType(**body.dict())
    db.add(device_type)
    db.commit()
    return DeviceTypeModel.from_orm(device_type)


@metrics_router.patch("/device_types/{device_type_id}", status_code=200, response_model=DeviceTypeModel)
async def patch_device_type(device_type_id: int, body: AddDeviceTypeModel, db: Session = Depends(get_db),
                            _=Depends(is_admin_permission)):
    device_type = db.query(DeviceType).filter_by(id=device_type_id).first()

    device_type.name = body.name
    db.add(device_type)
    db.commit()
    return DeviceTypeModel.from_orm(device_type)


@metrics_router.delete("/device_types/{device_type_id}/", status_code=200)
async def remove_device_type(device_type_id: int, db: Session = Depends(get_db)):
    db.query(DeviceType).filter_by(id=device_type_id).delete()
    db.commit()
    return ""
