from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db import Base


class Reading(Base):
    __tablename__ = 'readings'

    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String(255))
    value = Column(String(255))
    device_id = Column(Integer, ForeignKey('devices.id'))


class Device(Base):
    __tablename__ = 'devices'

    serial = Column(String(255), unique=True)
    model_number = Column(String(255))
    name = Column(String(255))
    description = Column(String(255), default='')
    manufacture_date = Column(DateTime, default=datetime.utcnow)
    type = Column(String(255), default='')

    room_id = Column(Integer, ForeignKey('building_floor_rooms.id'))
    readings = relationship(Reading, backref='device')


class Sensor(Base):
    __tablename__ = 'sensors'

    firmware_information = Column(String(255), default='')
    device_id = Column(Integer, ForeignKey('devices.id'), unique=True)
    device = relationship(Device)


class Meter(Base):
    __tablename__ = 'meters'

    device_id = Column(Integer, ForeignKey('devices.id'), unique=True)
    device = relationship(Device)

    sensors = relationship(Sensor, secondary='meter_sensor_binding')


class MeterSensorBinding(Base):
    __tablename__ = 'meter_sensor_binding'

    meter_id = Column(Integer, ForeignKey('meters.id'))
    sensor_id = Column(Integer, ForeignKey('sensors.id'))

    __tableargs__ = (UniqueConstraint('sensor_id', 'meter_id', name='_sensor_meter_uc'),)