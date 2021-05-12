from datetime import datetime
from typing import List, Optional

from fastapi import Depends, HTTPException, Header
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import MeterSnapshot, HeatMeterSnapshot, \
    ElectricityMeterSnapshot, MeterType, Meter
from permissions import is_admin_permission
from request_models.metrics_requests import MeterSnapshotModel, AddMeterSnapshotModel, ChangeMeterSnapshotModel, \
    AddAutoMeterSnapshotModel
from routes import metrics_router


@metrics_router.get("/meter-snapshots/", status_code=200, response_model=List[MeterSnapshotModel])
async def get_meter_snapshots(type_name: MeterType = '', date_start: datetime = None, date_end: datetime = None,
                              meter_id: int = 0, db: Session = Depends(get_db)):
    meter_snapshots = db.query(MeterSnapshot)
    if meter_id:
        meter_snapshots = meter_snapshots.filter(MeterSnapshot.meter_id == meter_id)
    if type_name:
        meter_snapshots = meter_snapshots.filter_by(type=type_name)
    if meter_id:
        meter_snapshots = meter_snapshots.filter_by(meter_id=meter_id)
    if date_start:
        meter_snapshots = meter_snapshots.filter(MeterSnapshot.creation_date >= date_start)
    if date_end:
        meter_snapshots = meter_snapshots.filter(MeterSnapshot.creation_date <= date_end)
    meter_snapshots = meter_snapshots.all()
    return [MeterSnapshotModel.from_orm(d) for d in meter_snapshots]


@metrics_router.post("/meter-snapshots/", status_code=201, response_model=MeterSnapshotModel)
async def add_meter_snapshot(body: AddMeterSnapshotModel, db: Session = Depends(get_db), ):
    snapshot_dict = body.dict()
    snapshot_dict['automatic'] = False
    heat_dict = snapshot_dict.pop('heat', {})
    electricity_dict = snapshot_dict.pop('electricity', {})

    meter_snapshot = MeterSnapshot(**snapshot_dict)

    if body.type == MeterType.Electricity:
        meter_snapshot.electricity_meter_snapshot = ElectricityMeterSnapshot(**electricity_dict)
    elif body.type == MeterType.Heat:
        meter_snapshot.heat_meter_snapshot = HeatMeterSnapshot(**heat_dict)

    db.add(meter_snapshot)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.post("/meter-snapshots/auto/", status_code=201, response_model=MeterSnapshotModel)
async def add_meter_snapshot_auto(body: AddAutoMeterSnapshotModel, db: Session = Depends(get_db),
                                  secret_key: str = Header(None)):
    meter = db.query(Meter).filter(Meter.secret_key == secret_key).first()
    if not meter:
        raise HTTPException(status_code=400, detail="Wrong secret key")
    automatic = True

    snapshot_dict = body.dict()
    snapshot_dict['automatic'] = automatic
    snapshot_dict['meter_id'] = meter.id
    heat_dict = snapshot_dict.pop('heat', {})
    electricity_dict = snapshot_dict.pop('electricity', {})

    meter_snapshot = MeterSnapshot(**snapshot_dict)

    if body.type == MeterType.Electricity:
        meter_snapshot.electricity_meter_snapshot = ElectricityMeterSnapshot(**electricity_dict)
    elif body.type == MeterType.Heat:
        meter_snapshot.heat_meter_snapshot = HeatMeterSnapshot(**heat_dict)

    db.add(meter_snapshot)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Bad info', status_code=400)

    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.patch("/meter-snapshots/{meter_snapshot_id}", status_code=200, response_model=MeterSnapshotModel)
async def patch_meter_snapshot(meter_snapshot_id: int, body: ChangeMeterSnapshotModel, db: Session = Depends(get_db),
                               _=Depends(is_admin_permission)):
    meter_snapshot = db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).first()

    previous_type = meter_snapshot.type

    snapshot_dict = body.dict(exclude_unset=True)
    heat_dict = snapshot_dict.pop('heat', {})
    electricity_dict = snapshot_dict.pop('electricity', {})

    args = {k: v for k, v in snapshot_dict.items()}
    for k, v in args.items():
        setattr(meter_snapshot, k, v)

    if meter_snapshot.type != previous_type:
        if previous_type == MeterType.Electricity:
            instance_to_delete = meter_snapshot.electricity_meter_snapshot
        elif previous_type == MeterType.Heat:
            instance_to_delete = meter_snapshot.heat_meter_snapshot
        else:
            #  previous_type == MeterType.Water
            instance_to_delete = meter_snapshot.water_meter_snapshot
        db.delete(instance_to_delete)

    if meter_snapshot.type == MeterType.Electricity:
        if meter_snapshot.electricity_meter_snapshot:
            for k, v in electricity_dict.items():
                setattr(meter_snapshot.electricity_meter_snapshot, k, v)
        else:
            meter_snapshot.electricity_meter_snapshot = ElectricityMeterSnapshot(**electricity_dict)
    elif meter_snapshot.type == MeterType.Heat:
        if meter_snapshot.heat_meter_snapshot:
            for k, v in heat_dict.items():
                setattr(meter_snapshot.heat_meter_snapshot, k, v)
        else:
            meter_snapshot.heat_meter_snapshot = HeatMeterSnapshot(**heat_dict)

    db.merge(meter_snapshot)
    db.commit()
    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.delete("/meter-snapshots/{meter_snapshot_id}/", status_code=200)
async def remove_meter_snapshot(meter_snapshot_id: int, db: Session = Depends(get_db)):
    db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).delete()
    db.commit()
    return ""
