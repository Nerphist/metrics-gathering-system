from datetime import datetime
from typing import List, Optional

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.metrics import Meter, Reading, ElectricityMeter, MeterSnapshot, HeatMeterSnapshot, \
    ElectricityMeterSnapshot, WaterMeterSnapshot
from request_models import make_change_model, make_add_model

ReadingModel = sqlalchemy_to_pydantic(Reading)
ElectricityMeterModel = sqlalchemy_to_pydantic(ElectricityMeter)
HeatMeterSnapshotModel = sqlalchemy_to_pydantic(HeatMeterSnapshot)
WaterMeterSnapshotModel = sqlalchemy_to_pydantic(WaterMeterSnapshot)
ElectricityMeterSnapshotModel = sqlalchemy_to_pydantic(ElectricityMeterSnapshot)


class MeterSnapshotModel(sqlalchemy_to_pydantic(MeterSnapshot)):
    heat_meter_snapshot: Optional[HeatMeterSnapshotModel]
    electricity_meter_snapshot: Optional[ElectricityMeterSnapshotModel]
    water_meter_snapshot: Optional[WaterMeterSnapshotModel]


class RecognizeMeterModel(BaseModel):
    meter_exists: bool


class MeterModel(sqlalchemy_to_pydantic(Meter)):
    readings: List[ReadingModel]
    electricity: Optional[ElectricityMeterModel]
    snapshots: List[MeterSnapshotModel]


class AddReadingModel(BaseModel):
    value: str
    type: str
    date: datetime = datetime.utcnow()


AddMeterModel = make_add_model(sqlalchemy_to_pydantic(Meter))
AddElectricityMeterModel = make_add_model(sqlalchemy_to_pydantic(ElectricityMeter))
AddMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(MeterSnapshot))
AddHeatMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(HeatMeterSnapshot))
AddElectricityMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(ElectricityMeterSnapshot))
AddWaterMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(WaterMeterSnapshot))

ChangeMeterModel = make_change_model(sqlalchemy_to_pydantic(Meter))
ChangeElectricityMeterModel = make_change_model(sqlalchemy_to_pydantic(ElectricityMeter))
ChangeMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(MeterSnapshot))
ChangeHeatMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(HeatMeterSnapshot))
ChangeElectricityMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(ElectricityMeterSnapshot))
ChangeWaterMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(WaterMeterSnapshot))
