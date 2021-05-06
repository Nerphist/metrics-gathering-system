from sqlalchemy import Column, String, Integer, UniqueConstraint, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from db import Base
from models.metrics import Meter


class BuildingType(Base):
    __tablename__ = 'building_types'

    name = Column(String(255), nullable=False, unique=True)
    buildings = relationship("Building", backref="building_type")


class Location(Base):
    __tablename__ = 'locations'

    name = Column(String(255), unique=True)
    longitude = Column(Numeric(), nullable=False, default=None)
    latitude = Column(Numeric(), nullable=False, default=None)
    buildings = relationship("Building", backref="location")
    __tableargs__ = (UniqueConstraint('longitude', 'latitude', name='_coordinates_uc'),)


class ResponsibleUser(Base):
    __tablename__ = 'responsible_users'

    user_id = Column(Integer)
    rank = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey('buildings.id'))
    responsibility = Column(String(255), nullable=True)


class Building(Base):
    __tablename__ = 'buildings'

    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    building_type_id = Column(Integer, ForeignKey('building_types.id', ondelete='CASCADE'), nullable=False)
    meters = relationship(Meter, backref="building")
    floors = relationship("Floor", backref="building")
    responsible_people = relationship("ResponsibleUser", backref="building")

    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    photo_document_id = Column(Integer, nullable=True)
    construction_type = Column(String, nullable=True)
    construction_year = Column(Integer, nullable=True)
    climate_zone = Column(String, nullable=True)

    heat_supply_contract_id = Column(Integer, nullable=True)
    electricity_supply_contract_id = Column(Integer, nullable=True)
    water_supply_contract_id = Column(Integer, nullable=True)

    operation_schedule = Column(String(255), nullable=True)
    operation_hours_per_year = Column(Integer, nullable=True)

    studying_daytime = Column(Integer, nullable=False, default=0)
    studying_evening_time = Column(Integer, nullable=False, default=0)
    studying_part_time = Column(Integer, nullable=False, default=0)
    working_teachers = Column(Integer, nullable=False, default=0)
    working_science = Column(Integer, nullable=False, default=0)
    working_help = Column(Integer, nullable=False, default=0)
    living_quantity = Column(Integer, nullable=False, default=0)

    utilized_space = Column(Numeric, nullable=True, default=None)
    utility_space = Column(Numeric, nullable=True, default=None)


class Floor(Base):
    __tablename__ = 'floors'

    building_id = Column(Integer, ForeignKey('buildings.id', ondelete='CASCADE'))
    index = Column(String(255), nullable=False)
    height = Column(Numeric, nullable=True, default=None)
    floor_plan_document_id = Column(Integer, nullable=True)
    rooms = relationship("Room", backref="floor")

    __tableargs__ = (UniqueConstraint('index', 'building_id', name='_building_floor_uc'),)


class Room(Base):
    __tablename__ = 'rooms'

    index = Column(String(255), nullable=False)
    floor_id = Column(Integer, ForeignKey('floors.id', ondelete='CASCADE'), nullable=False)
    designation = Column(String(255), nullable=True)
    size = Column(Numeric, nullable=True, default=None)
    responsible_department = Column(String(255), nullable=True)
