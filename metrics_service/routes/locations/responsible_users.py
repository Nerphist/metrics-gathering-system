from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_api import get_user
from db import get_db
from models import PermissionSet
from models.location import ResponsibleUser
from permissions import has_permission
from request_models import create_pagination_model
from request_models.location_requests import ResponsibleUserModel, AddResponsibleUserModel, ChangeResponsibleUserModel
from routes import metrics_router
from utils import apply_filtering


@metrics_router.get("/responsible_users/", status_code=200,
                    response_model=create_pagination_model(ResponsibleUserModel))
async def get_responsible_users(request: Request, db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingRead.value)
    result_models, count, page_number = apply_filtering(
        db=db,
        db_model=ResponsibleUser,
        request=request
    )

    items = [{'id': user.id, 'rank': user.rank, 'building_id': user.building_id, 'user': get_user(user.user_id)} for
             user in result_models]
    return {
        'total_size': count,
        'page_number': page_number,
        'page_size': len(items),
        'items': items
    }


@metrics_router.post("/responsible_users/", status_code=201, response_model=ResponsibleUserModel)
async def add_responsible_user(request: Request, body: AddResponsibleUserModel, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.BuildingEdit.value)
    if not (user := get_user(body.user_id)):
        raise HTTPException(detail='User does not exist', status_code=400)
    responsible_user = ResponsibleUser(**body.dict())
    db.add(responsible_user)
    db.commit()
    return {'id': responsible_user.id, 'rank': responsible_user.rank, 'building_id': responsible_user.building_id,
            'user': user}


@metrics_router.patch("/responsible_users/{responsible_user_id}", status_code=200, response_model=ResponsibleUserModel)
async def patch_responsible_user(request: Request, responsible_user_id: int, body: ChangeResponsibleUserModel,
                                 db: Session = Depends(get_db)):
    has_permission(request, PermissionSet.BuildingEdit.value)
    responsible_user = db.query(ResponsibleUser).filter_by(id=responsible_user_id).first()

    args = {k: v for k, v in body.dict(exclude_unset=True).items()}
    if args:
        for k, v in args.items():
            setattr(responsible_user, k, v)

        db.add(responsible_user)
        db.commit()
    return ResponsibleUserModel.from_orm(responsible_user)


@metrics_router.delete("/responsible_users/{responsible_user_id}/", status_code=200)
async def remove_responsible_user(request: Request, responsible_user_id: int, db: Session = Depends(get_db), ):
    has_permission(request, PermissionSet.BuildingEdit.value)
    db.query(ResponsibleUser).filter_by(id=responsible_user_id).delete()
    db.commit()
    return ""


@metrics_router.delete("/responsible_users/users/{user_id}/", status_code=200)
async def remove_responsible_user_by_user_id(request: Request, user_id: int, db: Session = Depends(get_db),):
    has_permission(request, PermissionSet.BuildingEdit.value)
    db.query(ResponsibleUser).filter_by(user_id=user_id).delete()
    db.commit()
    return ""
