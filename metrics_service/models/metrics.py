import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship

from db import Base


class MeterType(enum.Enum):
    Water = 'Water'
    Gas = 'Gas'
    Heat = 'Heat'
    Electricity = 'Electricity'


class ElectricityMeterSnapshot(Base):
    __tablename__ = 'electricity_meter_snapshots'

    snapshot_id = Column(Integer, ForeignKey('meter_snapshots.id', ondelete='CASCADE'), unique=True, nullable=False)
    snapshot = relationship('MeterSnapshot', back_populates='electricity_meter_snapshot')
    voltage = Column(Numeric, nullable=False)
    current = Column(Numeric, nullable=True)


class HeatMeterSnapshot(Base):
    __tablename__ = 'heat_meter_snapshots'

    snapshot_id = Column(Integer, ForeignKey('meter_snapshots.id', ondelete='CASCADE'), unique=True, nullable=False)
    snapshot = relationship('MeterSnapshot', back_populates='heat_meter_snapshot')
    incoming_temperature = Column(Numeric, nullable=True)
    outgoing_temperature = Column(Numeric, nullable=True)
    incoming_pump_usage = Column(Numeric, nullable=True)
    outgoing_pump_usage = Column(Numeric, nullable=True)
    outside_temperature = Column(Numeric, nullable=True)
    inside_temperature = Column(Numeric, nullable=True)
    incoming_water_pressure = Column(Numeric, nullable=True)
    outgoing_water_pressure = Column(Numeric, nullable=True)
    heat_consumption = Column(Numeric, nullable=True)


class MeterSnapshot(Base):
    __tablename__ = 'meter_snapshots'

    meter_id = Column(Integer, ForeignKey('meters.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(MeterType), nullable=False)
    consumption = Column(Numeric, nullable=False)
    automatic = Column(Boolean, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    current_time = Column(DateTime, nullable=True)
    uptime = Column(Numeric, nullable=True, default=None)

    heat_meter_snapshot = relationship(HeatMeterSnapshot, back_populates='snapshot', uselist=False)
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

    snapshots = relationship(MeterSnapshot, backref='meter')
    electricity = relationship('ElectricityMeter', back_populates='meter', uselist=False)

    secret_key = Column(String(255), default=uuid.uuid4, nullable=True)
    recognition_key = Column(String(255), default=uuid.uuid4, nullable=True)

    is_working = Column(Boolean, default=True)
    average_hours_per_day_usage = Column(Integer, nullable=True)
    average_days_per_week_usage = Column(Integer, nullable=True)


class ElectricityMeter(Base):
    __tablename__ = 'electricity_meters'

    meter_id = Column(Integer, ForeignKey('meters.id', ondelete='CASCADE'), nullable=False, unique=True)
    meter = relationship(Meter, back_populates='electricity')
    connection_type = Column(String(255), nullable=False)
    transformation_coefficient = Column(String(255), nullable=False)


class EnvironmentalReading(Base):
    __tablename__ = 'environmental_readings'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    automatic = Column(Boolean, nullable=True, default=True)
    current_time = Column(DateTime, nullable=False)
    temperature = Column(Numeric, nullable=True)
    humidity = Column(Numeric, nullable=True)
    notes = Column(String(255), nullable=True)
