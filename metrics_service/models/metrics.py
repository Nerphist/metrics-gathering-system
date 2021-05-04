import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db import Base


class Reading(Base):
    __tablename__ = 'readings'

    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String(255))
    value = Column(String(255))
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'))


class DeviceType(Base):
    __tablename__ = 'device_types'

    name = Column(String(255), nullable=False, unique=True)
    devices = relationship("Device", backref="device_type")


class Device(Base):
    __tablename__ = 'devices'

    serial = Column(String(255), unique=True)
    model_number = Column(String(255))
    name = Column(String(255))
    description = Column(String(255), default='')
    manufacture_date = Column(DateTime, default=datetime.utcnow)
    secret_key = Column(String(63), default=uuid.uuid4, index=True, unique=True)
    recognition_key = Column(String(63), default=uuid.uuid4, index=True, unique=True)

    device_type_id = Column(ForeignKey('device_types.id'), nullable=False)

    room_id = Column(Integer, ForeignKey('building_rooms.id', ondelete='SET NULL'))
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
