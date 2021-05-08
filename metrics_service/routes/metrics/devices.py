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
async def patch_meter(meter_id: int, body: ChangeMeterModel, db: Session = Depends(get_db),
                      _=Depends(is_admin_permission)):
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

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
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
