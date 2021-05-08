from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from auth_api import get_user
from db import get_db
from models.location import ResponsibleUser
from permissions import is_admin_permission
from request_models.location_requests import ResponsibleUserModel, AddResponsibleUserModel, ChangeResponsibleUserModel
from routes import metrics_router


@metrics_router.get("/responsible_users/", status_code=200, response_model=List[ResponsibleUserModel])
async def get_responsible_users(db: Session = Depends(get_db)):
    responsible_user_models = db.query(ResponsibleUser).all()

    return [{'id': user.id, 'name': user.name, 'user': get_user(user.user_id)} for user in responsible_user_models]


@metrics_router.post("/responsible_users/", status_code=201, response_model=ResponsibleUserModel)
async def add_responsible_user(body: AddResponsibleUserModel, db: Session = Depends(get_db),
                               _=Depends(is_admin_permission)):
    if not (user := get_user(body.user_id)):
        raise HTTPException(detail='User does not exist', status_code=400)
    responsible_user = ResponsibleUser(**body.dict())
    db.add(responsible_user)
    db.commit()
    return {'id': responsible_user.id, 'name': responsible_user.name, 'user': user}


@metrics_router.patch("/responsible_users/{responsible_user_id}", status_code=200, response_model=ResponsibleUserModel)
async def patch_responsible_user(responsible_user_id: int, body: ChangeResponsibleUserModel,
                                 db: Session = Depends(get_db), _=Depends(is_admin_permission)):
    responsible_user = db.query(ResponsibleUser).filter_by(id=responsible_user_id).first()

    args = {k: v for k, v in body.dict().items() if v}
    if args:
        for k, v in args.items():
            setattr(responsible_user, k, v)

        db.add(responsible_user)
        db.commit()
    return ResponsibleUserModel.from_orm(responsible_user)


@metrics_router.delete("/responsible_users/{responsible_user_id}/", status_code=200)
async def remove_responsible_user(responsible_user_id: int, db: Session = Depends(get_db),
                                  _=Depends(is_admin_permission)):
    db.query(ResponsibleUser).filter_by(id=responsible_user_id).delete()
    db.commit()
    return ""


@metrics_router.delete("/responsible_users/users/{user_id}/", status_code=200)
async def remove_responsible_user_by_user_id(user_id: int, db: Session = Depends(get_db),
                                             _=Depends(is_admin_permission)):
    db.query(ResponsibleUser).filter_by(user_id=user_id).delete()
    db.commit()
    return ""
