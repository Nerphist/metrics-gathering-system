from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.metrics import EnvironmentalReading
from permissions import has_permission
from request_models import create_pagination_model
from request_models.metrics_requests import EnvironmentalReadingModel, \
    AddEnvironmentalReadingModel, ChangeEnvironmentalReadingModel
from routes import metrics_router
from utils import paginate


@metrics_router.get("/rooms/environmental-readings/", status_code=200,
                    response_model=create_pagination_model(EnvironmentalReadingModel))
async def get_environmental_readings(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.RoomRead.value)
    return paginate(
        db=db,
        db_model=EnvironmentalReading,
        serializer=EnvironmentalReadingModel,
        request=request
    )


@metrics_router.post("/rooms/environmental-readings/", status_code=201, response_model=EnvironmentalReadingModel)
async def add_environmental_reading(request: Request, body: AddEnvironmentalReadingModel,
                                    db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.RoomEdit.value)
    environmental_reading = EnvironmentalReading(**body.dict())
    db.add(environmental_reading)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='EnvironmentalReading already exists', status_code=400)
    return EnvironmentalReadingModel.from_orm(environmental_reading)


@metrics_router.patch("/rooms/environmental-readings/{environmental_reading_id}", status_code=200,
                      response_model=EnvironmentalReadingModel)
async def patch_environmental_reading(request: Request, environmental_reading_id: int,
                                      body: ChangeEnvironmentalReadingModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.RoomEdit.value)
    environmental_reading = db.query(EnvironmentalReading).filter_by(id=environmental_reading_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(environmental_reading, k, v)

        db.add(environmental_reading)
        db.commit()
    return EnvironmentalReadingModel.from_orm(environmental_reading)


@metrics_router.delete("/rooms/environmental_readings/{environmental_reading_id}/", status_code=200)
async def remove_environmental_reading(request: Request, environmental_reading_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.RoomEdit.value)
    db.query(EnvironmentalReading).filter_by(id=environmental_reading_id).delete()
    db.commit()
    return ""
