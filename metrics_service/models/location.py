import enum

from sqlalchemy import Column, String, Integer, UniqueConstraint, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship

from db import Base
from models.metrics import Meter


class FloorItemType(enum.Enum):
    Room = 'Room'
    Meter = 'Meter'


class WindowType(enum.Enum):
    Wood = 'Wood'
    Plastic = 'Plastic'
    Aluminium = 'Aluminium'


class HeatingBatteryType(enum.Enum):
    CastIron = 'CastIron'
    Registered = 'Registered'
    Panel = 'Panel'
    Aluminium = 'Aluminium'


class WaterEquipmentType(enum.Enum):
    Toilet = 'Toilet'
    Bath = 'Bath'
    Shower = 'Shower'
    Pissoir = 'Pissoir'


class ElectricEquipmentGroup(enum.Enum):
    LabEquipment = 'LabEquipment'
    HouseholdEquipment = 'HouseholdEquipment'
    ComputerEquipment = 'ComputerEquipment'
    ClimateEquipment = 'ClimateEquipment'
    LightningEquipment = 'LightningEquipment'


class ElectricEquipmentType(enum.Enum):
    Engine = 'Engine'
    Workbench = 'Workbench'

    Fridge = 'Fridge'
    Microwave = 'Microwave'
    Kettle = 'Kettle'

    Monitor = 'Monitor'
    Tower = 'Tower'
    Printer = 'Printer'

    Conditioner = 'Conditioner'
    Heater = 'Heater'
    FanHeater = 'FanHeater'
    FanConvector = 'FanConvector'

    LED = 'LED'
    Halogen = 'Halogen'
    Fluorescent = 'Fluorescent'
    Incandescent = 'Incandescent'
    Luminescent = 'Luminescent'


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

    building_id = Column(Integer, ForeignKey('buildings.id', ondelete='CASCADE'), nullable=False)
    index = Column(String(255), nullable=False)
    height = Column(Numeric, nullable=True, default=None)
    floor_plan_document_id = Column(Integer, nullable=True)
    rooms = relationship("Room", backref="floor")
    items = relationship("FloorPlanItem", backref="floor")

    __tableargs__ = (UniqueConstraint('index', 'building_id', name='_building_floor_uc'),)


class FloorPlanItem(Base):
    __tablename__ = 'floor_items'

    floor_id = Column(Integer, ForeignKey('floors.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(FloorItemType), nullable=False)
    item_id = Column(Integer, nullable=False)
    position_x = Column(Numeric, nullable=False)
    position_y = Column(Numeric, nullable=False)


class Room(Base):
    __tablename__ = 'rooms'

    index = Column(String(255), nullable=False)
    floor_id = Column(Integer, ForeignKey('floors.id', ondelete='CASCADE'), nullable=False)
    designation = Column(String(255), nullable=True)
    size = Column(Numeric, nullable=True, default=None)
    responsible_department = Column(String(255), nullable=True)
    windows = relationship("Window", backref="room")
    heating_batteries = relationship("HeatingBattery", backref="room")
    water_equipment = relationship("WaterEquipment", backref="room")
    electric_equipment = relationship("ElectricEquipment", backref="room")
    environmental_readings = relationship('EnvironmentalReading', backref='room')


class Window(Base):
    __tablename__ = 'windows'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(WindowType), nullable=False)
    thickness = Column(Numeric, nullable=True)
    glazing_formula = Column(String(255), nullable=True)


class HeatingBattery(Base):
    __tablename__ = 'heating_batteries'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(HeatingBatteryType), nullable=False)
    sections = Column(Integer, nullable=True)


class WaterEquipment(Base):
    __tablename__ = 'water_equipment'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(WaterEquipmentType), nullable=False)


class ElectricEquipment(Base):
    __tablename__ = 'electric_equipment'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    group = Column(Enum(ElectricEquipmentGroup), nullable=False)
    type = Column(Enum(ElectricEquipmentType), nullable=False)
    power_per_unit = Column(Numeric, nullable=True)
    subtype = Column(String(255), nullable=True)
