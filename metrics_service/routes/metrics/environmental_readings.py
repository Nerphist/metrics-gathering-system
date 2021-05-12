from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import EnvironmentalReading
from permissions import is_admin_permission
from request_models.metrics_requests import EnvironmentalReadingModel, \
    AddEnvironmentalReadingModel, ChangeEnvironmentalReadingModel
from routes import metrics_router


@metrics_router.get("/rooms/environmental-readings/", status_code=200, response_model=List[EnvironmentalReadingModel])
async def get_environmental_readings(room_id: int = 0, db: Session = Depends(get_db)):
    environmental_readings = db.query(EnvironmentalReading)
    if room_id:
        environmental_readings = environmental_readings.filter_by(room_id=room_id)
    return [EnvironmentalReadingModel.from_orm(b) for b in environmental_readings]


@metrics_router.post("/rooms/environmental-readings/", status_code=201, response_model=EnvironmentalReadingModel)
async def add_environmental_reading(body: AddEnvironmentalReadingModel, db: Session = Depends(get_db),
                                    _=Depends(is_admin_permission)):
    environmental_reading = EnvironmentalReading(**body.dict())
    db.add(environmental_reading)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='EnvironmentalReading already exists', status_code=400)
    return EnvironmentalReadingModel.from_orm(environmental_reading)


@metrics_router.patch("/rooms/environmental-readings/{environmental_reading_id}", status_code=200,
                      response_model=EnvironmentalReadingModel)
async def patch_environmental_reading(environmental_reading_id: int, body: ChangeEnvironmentalReadingModel,
                                      db: Session = Depends(get_db),
                                      _=Depends(is_admin_permission)):
    environmental_reading = db.query(EnvironmentalReading).filter_by(id=environmental_reading_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(environmental_reading, k, v)

        db.add(environmental_reading)
        db.commit()
    return EnvironmentalReadingModel.from_orm(environmental_reading)


@metrics_router.delete("/rooms/environmental_readings/{environmental_reading_id}/", status_code=200)
async def remove_environmental_reading(environmental_reading_id: int, db: Session = Depends(get_db),
                                       _=Depends(is_admin_permission)):
    db.query(EnvironmentalReading).filter_by(id=environmental_reading_id).delete()
    db.commit()
    return ""
