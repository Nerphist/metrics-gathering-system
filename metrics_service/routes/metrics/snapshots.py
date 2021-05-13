from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.metrics import MeterSnapshot, HeatMeterSnapshot, \
    ElectricityMeterSnapshot, MeterType, Meter
from permissions import has_permission
from request_models import create_pagination_model
from request_models.metrics_requests import MeterSnapshotModel, AddMeterSnapshotModel, ChangeMeterSnapshotModel, \
    AddAutoMeterSnapshotModel
from routes import metrics_router
from utils import paginate


@metrics_router.get("/meter-snapshots/", status_code=200, response_model=create_pagination_model(MeterSnapshotModel))
async def get_meter_snapshots(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.MeterSnapshotRead.value)
    return paginate(
        db=db,
        db_model=MeterSnapshot,
        serializer=MeterSnapshotModel,
        request=request
    )


@metrics_router.post("/meter-snapshots/", status_code=201, response_model=MeterSnapshotModel)
async def add_meter_snapshot(request: Request, body: AddMeterSnapshotModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.MeterSnapshotEdit.value)
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
async def patch_meter_snapshot(request: Request, meter_snapshot_id: int, body: ChangeMeterSnapshotModel,
                               db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.MeterSnapshotEdit.value)
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
async def remove_meter_snapshot(request: Request, meter_snapshot_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.MeterSnapshotEdit.value)
    db.query(MeterSnapshot).filter_by(id=meter_snapshot_id).delete()
    db.commit()
    return ""
