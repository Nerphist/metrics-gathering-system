from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.location import Building, Location
from permissions import is_admin_permission
from request_models.location_requests import LocationModel, AddLocationModel, ChangeLocationModel, HeadcountModel
from routes import metrics_router


@metrics_router.get("/headcount/", status_code=200, response_model=HeadcountModel)
async def get_headcount(db: Session = Depends(get_db)):
    buildings: List[Building] = db.query(Building).all()
    model = HeadcountModel()
    for building in buildings:
        model.living += building.living_quantity
        studying = building.studying_daytime + building.studying_evening_time + building.studying_part_time
        working = building.working_help + building.working_science + building.working_teachers
        model.studying += studying
        model.personnel += working
    return model


@metrics_router.get("/locations/", status_code=200, response_model=List[LocationModel])
async def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return [LocationModel.from_orm(b) for b in locations]


@metrics_router.post("/locations/", status_code=201, response_model=LocationModel)
async def add_location(body: AddLocationModel, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    location = Location(name=body.name, latitude=body.latitude, longitude=body.longitude)
    db.add(location)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Location already exists', status_code=400)
    return LocationModel.from_orm(location)


@metrics_router.patch("/locations/{location_id}", status_code=200, response_model=LocationModel)
async def patch_location(location_id: int, body: ChangeLocationModel, db: Session = Depends(get_db),
                         _=Depends(is_admin_permission)):
    location = db.query(Location).filter_by(id=location_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(location, k, v)

        db.add(location)
        db.commit()
    return LocationModel.from_orm(location)


@metrics_router.delete("/locations/{location_id}/", status_code=200)
async def remove_location(location_id: int, db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    db.query(Location).filter_by(id=location_id).delete()
    db.commit()
    return ""
