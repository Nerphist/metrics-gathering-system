from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.metrics import MeterSnapshot, HeatMeterSnapshot, WaterMeterSnapshot, \
    ElectricityMeterSnapshot, MeterType
from permissions import is_admin_permission
from request_models.metrics_requests import MeterSnapshotModel, AddMeterSnapshotModel, ChangeMeterSnapshotModel, \
    HeatMeterSnapshotModel, AddHeatMeterSnapshotModel, ChangeHeatMeterSnapshotModel, WaterMeterSnapshotModel, \
    AddWaterMeterSnapshotModel, ChangeWaterMeterSnapshotModel, ElectricityMeterSnapshotModel, \
    AddElectricityMeterSnapshotModel, ChangeElectricityMeterSnapshotModel
from routes import metrics_router


@metrics_router.get("/meter-snapshots/", status_code=200, response_model=List[MeterSnapshotModel])
async def get_meter_snapshots(meter_id: int = 0, db: Session = Depends(get_db)):
    meter_snapshots = db.query(MeterSnapshot)
    if meter_id:
        meter_snapshots = meter_snapshots.filter(MeterSnapshot.meter_id == meter_id)
    meter_snapshots = meter_snapshots.all()
    return [MeterSnapshotModel.from_orm(d) for d in meter_snapshots]


@metrics_router.post("/meter-snapshots/", status_code=201, response_model=MeterSnapshotModel)
async def add_meter_snapshot(body: AddMeterSnapshotModel, db: Session = Depends(get_db)):
    snapshot_dict = body.dict()
    heat_dict = snapshot_dict.pop('heat', {})
    water_dict = snapshot_dict.pop('water', {})
    electricity_dict = snapshot_dict.pop('electricity', {})

    meter_snapshot = MeterSnapshot(**snapshot_dict)

    if body.type == MeterType.Electricity:
        meter_snapshot.electricity_meter_snapshot = ElectricityMeterSnapshot(**electricity_dict)
    elif body.type == MeterType.Heat:
        meter_snapshot.heat_meter_snapshot = HeatMeterSnapshot(**heat_dict)
    elif body.type == MeterType.Water:
        meter_snapshot.water_meter_snapshot = WaterMeterSnapshot(**water_dict)

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
    water_dict = snapshot_dict.pop('water', {})
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
    elif meter_snapshot.type == MeterType.Water:
        if meter_snapshot.water_meter_snapshot:
            for k, v in water_dict.items():
                setattr(meter_snapshot.water_meter_snapshot, k, v)
        else:
            meter_snapshot.water_meter_snapshot = WaterMeterSnapshot(**water_dict)

    db.merge(meter_snapshot)
    db.commit()
    return MeterSnapshotModel.from_orm(meter_snapshot)


@metrics_router.delete("/meter-snapshots/{meter_snapshot_id}/", status_code=200)
async def remove_meter_snapshot(meter_snapshot_id: int, db: Session = Depends(get_db)):
    db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).delete()
    db.commit()
    return ""
