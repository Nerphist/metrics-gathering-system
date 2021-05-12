from datetime import datetime
from typing import List, Optional

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.metrics import Meter, ElectricityMeter, MeterSnapshot, HeatMeterSnapshot, \
    ElectricityMeterSnapshot, EnvironmentalReading
from request_models import make_change_model, make_add_model

ElectricityMeterModel = sqlalchemy_to_pydantic(ElectricityMeter)
HeatMeterSnapshotModel = sqlalchemy_to_pydantic(HeatMeterSnapshot)
ElectricityMeterSnapshotModel = sqlalchemy_to_pydantic(ElectricityMeterSnapshot)
EnvironmentalReadingModel = sqlalchemy_to_pydantic(EnvironmentalReading)


class MeterSnapshotModel(sqlalchemy_to_pydantic(MeterSnapshot)):
    heat_meter_snapshot: Optional[HeatMeterSnapshotModel]
    electricity_meter_snapshot: Optional[ElectricityMeterSnapshotModel]


class RecognizeMeterModel(BaseModel):
    meter_exists: bool


class MeterModel(sqlalchemy_to_pydantic(Meter)):
    electricity: Optional[ElectricityMeterModel]
    snapshots: List[MeterSnapshotModel]


class AddReadingModel(BaseModel):
    value: str
    type: str
    date: datetime = datetime.utcnow()


class AddElectricityMeterModel(BaseModel):
    connection_type: str
    transformation_coefficient: str


ChangeElectricityMeterModel = make_change_model(AddElectricityMeterModel)


class ChangeMeterModel(make_change_model(sqlalchemy_to_pydantic(Meter))):
    electricity: Optional[AddElectricityMeterModel]


class AddMeterModel(make_add_model(sqlalchemy_to_pydantic(Meter))):
    electricity: Optional[AddElectricityMeterModel]


AddHeatMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(HeatMeterSnapshot))
AddElectricityMeterSnapshotModel = make_add_model(sqlalchemy_to_pydantic(ElectricityMeterSnapshot))
AddEnvironmentalReadingModel = make_add_model(sqlalchemy_to_pydantic(EnvironmentalReading),
                                              fields_to_remove=['automatic'])


class AddMeterSnapshotModel(make_add_model(sqlalchemy_to_pydantic(MeterSnapshot), fields_to_remove=['automatic'])):
    heat: Optional[AddHeatMeterSnapshotModel]
    electricity: Optional[AddElectricityMeterSnapshotModel]


class AddAutoMeterSnapshotModel(make_add_model(sqlalchemy_to_pydantic(MeterSnapshot),
                                               fields_to_remove=['automatic', 'meter_id'])):
    heat: Optional[AddHeatMeterSnapshotModel]
    electricity: Optional[AddElectricityMeterSnapshotModel]


ChangeHeatMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(HeatMeterSnapshot))
ChangeElectricityMeterSnapshotModel = make_change_model(sqlalchemy_to_pydantic(ElectricityMeterSnapshot))
ChangeEnvironmentalReadingModel = make_change_model(sqlalchemy_to_pydantic(EnvironmentalReading),
                                                    fields_to_remove=['room_id', 'automatic'])


class ChangeMeterSnapshotModel(make_change_model(sqlalchemy_to_pydantic(MeterSnapshot),
                                                 fields_to_remove=['meter_id', 'automatic'])):
    heat: Optional[ChangeHeatMeterSnapshotModel]
    electricity: Optional[ChangeElectricityMeterSnapshotModel]
