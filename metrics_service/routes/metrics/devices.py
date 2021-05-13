from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.metrics import Meter, ElectricityMeter, MeterType
from permissions import has_permission
from request_models import create_pagination_model
from request_models.metrics_requests import MeterModel, AddMeterModel, \
    RecognizeMeterModel, ChangeMeterModel
from routes import metrics_router
from utils import paginate


@metrics_router.get("/meters/recognize/{recognition_key}/", status_code=201, response_model=RecognizeMeterModel)
async def recognize_meter(recognition_key: str, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.recognition_key == recognition_key).first()
    if not meter:
        return {'meter_exists': False}
    return {'meter_exists': True}


@metrics_router.get("/meters/", status_code=200, response_model=create_pagination_model(MeterModel))
async def get_meters(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.MeterRead.value)
    return paginate(
        db=db,
        db_model=Meter,
        serializer=MeterModel,
        request=request
    )


@metrics_router.post("/meters/", status_code=201, response_model=MeterModel)
async def add_meter(request: Request, body: AddMeterModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.MeterEdit.value)
    meter_dict = body.dict()
    electricity = None
    if body.type == MeterType.Electricity:
        electricity_dict = meter_dict.pop('electricity', None)
        if electricity_dict:
            electricity = ElectricityMeter(**electricity_dict)
        else:
            raise HTTPException(detail='Electricity info is needed', status_code=400)

    meter = Meter(**meter_dict)
    meter.electricity = electricity
    db.add(meter)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return MeterModel.from_orm(meter)


@metrics_router.patch("/meters/{meter_id}", status_code=200, response_model=MeterModel)
async def patch_meter(request: Request, meter_id: int, body: ChangeMeterModel, db: Session = Depends(get_db),):
    has_permission(request, PermissionSet.MeterEdit.value)
    meter = db.query(Meter).filter_by(id=meter_id).first()

    change_dict = body.dict(exclude_unset=True)
    electricity_dict = change_dict.pop('electricity', None)
    args = {k: v for k, v in change_dict.items()}
    for k, v in args.items():
        setattr(meter, k, v)

    if meter.type == MeterType.Electricity:
        if electricity_dict:
            if meter.electricity:
                for k, v in electricity_dict.items():
                    setattr(meter.electricity, k, v)
            else:
                electricity = ElectricityMeter(**electricity_dict)
                meter.electricity = electricity
        elif not meter.electricity:
            raise HTTPException(detail='Electricity info is needed', status_code=400)

    elif meter.electricity:
        db.query(ElectricityMeter).filter_by(id=meter.electricity.id).delete()
        meter.electricity = None

    db.merge(meter)
    db.commit()
    return MeterModel.from_orm(meter)


@metrics_router.delete("/meters/{meter_id}/", status_code=200)
async def remove_meter(request: Request, meter_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.MeterEdit.value)
    db.query(Meter).filter_by(id=meter_id).delete()
    db.commit()
    return ""
