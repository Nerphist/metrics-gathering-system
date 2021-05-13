from typing import List

from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import PermissionSet
from models.location import Building, Location
from permissions import has_permission
from request_models import create_pagination_model
from request_models.location_requests import LocationModel, AddLocationModel, ChangeLocationModel, HeadcountModel
from routes import metrics_router
from utils import paginate


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


@metrics_router.get("/locations/", status_code=200, response_model=create_pagination_model(LocationModel))
async def get_locations(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.LocationRead.value)
    return paginate(
        db=db,
        db_model=Location,
        serializer=LocationModel,
        request=request
    )


@metrics_router.post("/locations/", status_code=201, response_model=LocationModel)
async def add_location(request: Request, body: AddLocationModel, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.LocationEdit.value)
    location = Location(name=body.name, latitude=body.latitude, longitude=body.longitude)
    db.add(location)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Location already exists', status_code=400)
    return LocationModel.from_orm(location)


@metrics_router.patch("/locations/{location_id}", status_code=200, response_model=LocationModel)
async def patch_location(request: Request, location_id: int, body: ChangeLocationModel,
                         db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.LocationEdit.value)
    location = db.query(Location).filter_by(id=location_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(location, k, v)

        db.add(location)
        db.commit()
    return LocationModel.from_orm(location)


@metrics_router.delete("/locations/{location_id}/", status_code=200)
async def remove_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.LocationEdit.value)
    db.query(Location).filter_by(id=location_id).delete()
    db.commit()
    return ""
