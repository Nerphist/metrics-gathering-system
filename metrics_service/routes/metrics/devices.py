from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import Meter, ElectricityMeter, MeterType
from permissions import is_admin_permission
from request_models.metrics_requests import MeterModel, AddMeterModel, \
    RecognizeMeterModel, ChangeMeterModel, AddElectricityMeterModel, \
    ElectricityMeterModel, ChangeElectricityMeterModel
from routes import metrics_router


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


@metrics_router.post("/electricity-meters/", status_code=201, response_model=ElectricityMeterModel)
async def add_electricity_meter(body: AddElectricityMeterModel, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter_by(id=body.meter_id).first()
    if not meter:
        raise HTTPException(detail='Meter does not exist', status_code=404)
    if meter.type != MeterType.Electricity:
        raise HTTPException(detail='Meter type is not electricity', status_code=400)

    electricity_meter = ElectricityMeter(**body.dict())
    try:
        db.add(electricity_meter)
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return ElectricityMeterModel.from_orm(electricity_meter)


@metrics_router.patch("/electricity-meters/{electricity_meter_id}", status_code=200,
                      response_model=ElectricityMeterModel)
async def patch_electricity_meter(electricity_meter_id: int,
                                  body: ChangeElectricityMeterModel,
                                  db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    electricity_meter = db.query(ElectricityMeter).filter_by(id=electricity_meter_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(electricity_meter, k, v)

        db.add(electricity_meter)
        db.commit()
    return ElectricityMeterModel.from_orm(electricity_meter)


@metrics_router.delete("/electricity-meters/{electricity_meter_id}/", status_code=200)
async def remove_electricity_meter(electricity_meter_id: int, db: Session = Depends(get_db)):
    db.query(ElectricityMeter).filter_by(id=electricity_meter_id).delete()
    db.commit()
    return ""
