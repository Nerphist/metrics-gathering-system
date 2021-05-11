from datetime import datetime
from typing import List, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import Reading, Meter
from request_models.metrics_requests import ReadingModel, AddReadingModel
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
