import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship

from db import Base


class MeterType(enum.Enum):
    Water = 'Water'
    Gas = 'Gas'
    Heat = 'Heat'
    Electricity = 'Electricity'


class Reading(Base):
    __tablename__ = 'readings'

    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String(255))
    value = Column(String(255))
    meter_id = Column(Integer, ForeignKey('meters.id', ondelete='CASCADE'))


class WaterMeterSnapshot(Base):
    __tablename__ = 'water_meter_snapshots'

    snapshot_id = Column(Integer, ForeignKey('meter_snapshots.id', ondelete='CASCADE'), unique=True, nullable=False)
    snapshot = relationship('MeterSnapshot', back_populates='water_meter_snapshot')
    consumption = Column(Numeric, nullable=False, default=None)


class ElectricityMeterSnapshot(Base):
    __tablename__ = 'electricity_meter_snapshots'

    snapshot_id = Column(Integer, ForeignKey('meter_snapshots.id', ondelete='CASCADE'), unique=True, nullable=False)
    snapshot = relationship('MeterSnapshot', back_populates='electricity_meter_snapshot')
    current_voltage = Column(Numeric, nullable=False, default=None)


class HeatMeterSnapshot(Base):
    __tablename__ = 'heat_meter_snapshots'

    snapshot_id = Column(Integer, ForeignKey('meter_snapshots.id', ondelete='CASCADE'), unique=True, nullable=False)
    snapshot = relationship('MeterSnapshot', back_populates='heat_meter_snapshot')
    current_voltage = Column(Numeric, nullable=False, default=None)


class MeterSnapshot(Base):
    __tablename__ = 'meter_snapshots'

    meter_id = Column(Integer, ForeignKey('meters.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(MeterType), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    current_time = Column(DateTime, nullable=True)
    uptime = Column(Numeric, nullable=True, default=None)

    heat_meter_snapshot = relationship(HeatMeterSnapshot, back_populates='snapshot', uselist=False)
    water_meter_snapshot = relationship(WaterMeterSnapshot, back_populates='snapshot', uselist=False)
    electricity_meter_snapshot = relationship(ElectricityMeterSnapshot, back_populates='snapshot', uselist=False)


class Meter(Base):
    __tablename__ = 'meters'

    building_id = Column(Integer, ForeignKey('buildings.id', ondelete='SET NULL'), nullable=True)
    type = Column(Enum(MeterType), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False)
    model_number = Column(String(255), nullable=False)
    number = Column(String(255), nullable=True)
    manufacture_year = Column(Integer, nullable=False)
    installation_date = Column(DateTime, nullable=True)
    installation_notes = Column(String(255), nullable=True)
    accounting_number = Column(String(255), nullable=True)
    related_contract_number = Column(String(255), nullable=True)
    last_verification_date = Column(DateTime, nullable=True)
    responsible_user_id = Column(Integer, nullable=True)
    other_notes = Column(String(255), nullable=True)
    verification_interval_sec = Column(Integer, nullable=True)

    readings = relationship(Reading, backref='meter')
    snapshots = relationship(MeterSnapshot, backref='meter')
    electricity = relationship('ElectricityMeter', back_populates='meter', uselist=False)

    secret_key = Column(String(255), default=uuid.uuid4, nullable=True)
    recognition_key = Column(String(255), default=uuid.uuid4, nullable=True)


class ElectricityMeter(Base):
    __tablename__ = 'electricity_meters'

    meter_id = Column(Integer, ForeignKey('meters.id', ondelete='CASCADE'), nullable=False, unique=True)
    meter = relationship(Meter, back_populates='electricity')
    connection_type = Column(String(255), nullable=False)
    transformation_coefficient = Column(String(255), nullable=False)
