from datetime import datetime
from typing import List, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import Reading, Meter, MeterSnapshot
from permissions import is_admin_permission
from request_models.metrics_requests import ReadingModel, AddReadingModel, MeterModel, AddMeterModel, \
    RecognizeMeterModel, ChangeMeterModel, MeterSnapshotModel, AddMeterSnapshotModel, ChangeMeterSnapshotModel
from routes import metrics_router


@metrics_router.get("/readings/", status_code=200, response_model=List[ReadingModel])
async def get_readings(type_name: str = '', date_start: str = '', date_end: str = '', meter_id: int = 0,
                       db: Session = Depends(get_db)):
    readings = db.query(Reading)
    if type_name:
        readings = readings.filter_by(type=type_name)
    if meter_id:
        readings = readings.filter_by(meter_id=meter_id)
    if date_start:
        date_start_formatted = datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%S")
        readings = readings.filter(Reading.date >= date_start_formatted)
    if date_end:
        date_end_formatted = datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S")
        readings = readings.filter(Reading.date <= date_end_formatted)
    readings = readings.all()
    return [ReadingModel.from_orm(r) for r in readings]


@metrics_router.post("/readings/", status_code=201, response_model=ReadingModel)
async def add_reading(body: AddReadingModel, db: Session = Depends(get_db), secret_key: Optional[str] = Header(None)):
    reading = Reading(body.dict())
    meter = db.query(Meter).filter(Meter.secret_key == secret_key).first()
    if not meter:
        raise HTTPException(status_code=400, detail="Wrong secret key")

    reading.meter_id = meter.id
    try:
        db.add(reading)
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return ReadingModel.from_orm(reading)


@metrics_router.get("/meters/recognize/{recognition_key}/", status_code=201, response_model=RecognizeMeterModel)
async def recognize_meter(recognition_key: str, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.recognition_key == recognition_key).first()
    if not meter:
        return {'meter_exists': False}
    return {'meter_exists': True}


@metrics_router.get("/meters/", status_code=200, response_model=List[MeterModel])
async def get_meters(building_id: int = 0, db: Session = Depends(get_db)):
    meters = db.query(Meter)
    if building_id:
        meters = meters.filter(Meter.building_id == building_id)
    meters = meters.all()
    return [MeterModel.from_orm(d) for d in meters]


@metrics_router.post("/meters/", status_code=201, response_model=MeterModel)
async def add_meter(body: AddMeterModel, db: Session = Depends(get_db)):
    meter = Meter(**body.dict())
    db.add(meter)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return MeterModel.from_orm(meter)


@metrics_router.patch("/meters/{meter_id}", status_code=200, response_model=MeterModel)
async def patch_meter(meter_id: int, body: ChangeMeterModel, db: Session = Depends(get_db),
                      _=Depends(is_admin_permission)):
    meter = db.query(Meter).filter_by(id=meter_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(meter, k, v)

        db.add(meter)
        db.commit()
    return MeterModel.from_orm(meter)


@metrics_router.delete("/meters/{meter_id}/", status_code=200)
async def remove_meter(meter_id: int, db: Session = Depends(get_db)):
    db.query(Meter).filter_by(id=meter_id).delete()
    db.commit()
    return ""


@metrics_router.get("/meter_snapshots/", status_code=200, response_model=List[MeterSnapshotModel])
async def get_meter_snapshots(building_id: int = 0, db: Session = Depends(get_db)):
    meter_snapshots = db.query(MeterSnapshot)
    if building_id:
        meter_snapshots = meter_snapshots.filter(MeterSnapshot.building_id == building_id)
    meter_snapshots = meter_snapshots.all()
    return [MeterSnapshotModel.from_orm(d) for d in meter_snapshots]


@metrics_router.post("/meter_snapshots/", status_code=201, response_model=MeterSnapshotModel)
async def add_meter_snapshot(body: AddMeterSnapshotModel, db: Session = Depends(get_db)):
    meter_snapshot = MeterSnapshot(**body.dict())
    try:
        db.add(meter_snapshot)
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.patch("/meter_snapshots/{meter_snapshot_id}", status_code=200, response_model=MeterSnapshotModel)
async def patch_meter_snapshot(meter_snapshot_id: int, body: ChangeMeterSnapshotModel, db: Session = Depends(get_db),
                               _=Depends(is_admin_permission)):
    meter_snapshot = db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(meter_snapshot, k, v)

        db.add(meter_snapshot)
        db.commit()
    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.delete("/meter_snapshots/{meter_snapshot_id}/", status_code=200)
async def remove_meter_snapshot(meter_snapshot_id: int, db: Session = Depends(get_db)):
    db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).delete()
    db.commit()
    return ""
