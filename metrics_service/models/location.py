from sqlalchemy import Column, String, Integer, UniqueConstraint, ForeignKey, Numeric
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
    rooms = relationship("Room", backref="building")
    responsible_users = relationship("ResponsibleUser", backref="building")

    building_type_id = Column(Integer, ForeignKey('building_types.id', ondelete='CASCADE'))

    name = Column(String)
    description = Column(String)

    living_quantity = Column(Integer, nullable=False, default=0)
    studying_daytime = Column(Integer, nullable=False, default=0)
    studying_evening_time = Column(Integer, nullable=False, default=0)
    studying_part_time = Column(Integer, nullable=False, default=0)
    working_teachers = Column(Integer, nullable=False, default=0)
    working_science = Column(Integer, nullable=False, default=0)
    working_help = Column(Integer, nullable=False, default=0)

    construction_year = Column(Integer)
    last_capital_repair_year = Column(Integer)
    building_index = Column(String)
    address = Column(String)


class Room(Base):
    __tablename__ = 'building_rooms'

    name = Column(String(255))
    building_id = Column(Integer, ForeignKey('buildings.id'))
    size = Column(Numeric)
    designation = Column(String(255))
    responsible_department = Column(String(255))
    devices = relationship(Device, backref="room")
    __tableargs__ = (UniqueConstraint('name', 'building_id', name='_building_room_name_uc'),)
