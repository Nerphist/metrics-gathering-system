from sqlalchemy import Column, String, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.metrics import Device


class BuildingType(Base):
    __tablename__ = 'building_types'

    name = Column(String(255), nullable=False, unique=True)
    buildings = relationship("Building", backref="building_type")


class Location(Base):
    __tablename__ = 'locations'

    name = Column(String(255), unique=True)
    longitude = Column(String(255))
    latitude = Column(String(255))
    buildings = relationship("Building", backref="location")
    __tableargs__ = (UniqueConstraint('longitude', 'latitude', name='_coordinates_uc'),)


class ResponsibleUser(Base):
    __tablename__ = 'responsible_users'

    user_id = Column(Integer)
    name = Column(String(255))
    building_id = Column(Integer, ForeignKey('buildings.id'))


class Building(Base):
    __tablename__ = 'buildings'

    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'))
    floors = relationship("Floor", backref="building")
    responsible_users = relationship("ResponsibleUser", backref="building")

    building_type_id = Column(Integer, ForeignKey('building_types.id', ondelete='CASCADE'))

    name = Column(String)
    description = Column(String)

    construction_year = Column(Integer)
    last_capital_repair_year = Column(Integer)
    building_index = Column(String)
    address = Column(String)


class Floor(Base):
    __tablename__ = 'building_floors'

    number = Column(Integer)
    building_id = Column(Integer, ForeignKey('buildings.id'))
    rooms = relationship("Room", backref="floor")
    __tableargs__ = (UniqueConstraint('number', 'building_id', name='_building_floor_number_uc'),)


class Room(Base):
    __tablename__ = 'building_floor_rooms'

    name = Column(String(255))
    floor_id = Column(Integer, ForeignKey('building_floors.id'))
    devices = relationship(Device, backref="room")
    __tableargs__ = (UniqueConstraint('name', 'floor_id', name='_floor_room_name_uc'),)
