from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.tasks import Task, TaskNote
from request_models.tasks import TaskModel, AddTaskModel, AddTaskNoteModel, TaskNoteModel, AlterTaskModel
from routes import tasks_router


@tasks_router.get("/status/", status_code=200)
async def get_tasks_status():
    return {
        'status': 'info',
        'header': 'Everything is fine',
        'message': 'Tasks are properly performed.'
    }


@tasks_router.get("/weekly-report/", status_code=200)
async def get_tasks_status():
    return {
        'Mon': 0,
        'Tue': 4,
        'Wed': 3,
        'Thu': 5,
        'Fri': 6,
        'Sat': 8,
        'Sun': 10,
    }


@tasks_router.get("/", status_code=200, response_model=List[TaskModel])
async def get_tasks(db: Session = Depends(get_db), creator_id: int = None, assignee_id: int = None):
    tasks = db.query(Task)

    if creator_id:
        tasks = tasks.filter(Task.creator_id == creator_id)

    if assignee_id:
        tasks = tasks.filter(Task.assignee_id == assignee_id)

    tasks = tasks.all()
    return [TaskModel.from_orm(b) for b in tasks]


@tasks_router.post("/", status_code=201, response_model=TaskModel)
async def add_task(body: AddTaskModel, db: Session = Depends(get_db)):
    task = Task(**body.dict())
    existing_priorities = db.query(Task.priority).filter(Task.assignee_id == task.assignee_id,
                                                         Task.creator_id == task.creator_id).all()
    priorities_list = [r[0] for r in existing_priorities]
    if not task.priority or task.priority in priorities_list:
        task.priority = max(priorities_list, default=0) + 1
    db.add(task)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Task already exists', status_code=400)
    return TaskModel.from_orm(task)


@tasks_router.patch("/{task_id}/", status_code=200, response_model=TaskModel)
async def alter_task(body: AlterTaskModel, task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    for key, val in body.dict().items():
        if val is not None:
            setattr(task, key, val)

    db.merge(task)
    try:
        db.commit()
    except IntegrityError as e:
        raise HTTPException(detail=f'Exception on altering task {str(e)}', status_code=400)
    return TaskModel.from_orm(task)


@tasks_router.delete("/{task_id}/", status_code=200)
async def remove_task(task_id: int, db: Session = Depends(get_db)):
    db.query(Task).filter_by(id=task_id).delete()
    db.commit()
    return ""


@tasks_router.get("/notes/{task_id}/", status_code=200, response_model=List[TaskNoteModel])
async def get_task_notes(task_id: int, db: Session = Depends(get_db)):
    tasks = db.query(TaskNote).filter_by(task_id=task_id).all()
    return [TaskNoteModel.from_orm(b) for b in tasks]


@tasks_router.post("/notes/", status_code=201, response_model=TaskNoteModel)
async def add_task_note(body: AddTaskNoteModel, db: Session = Depends(get_db)):
    note = TaskNote(**body.dict())
    db.add(note)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(detail='Task already exists', status_code=400)
    return TaskNoteModel.from_orm(note)


@tasks_router.delete("/notes/{note_id}/", status_code=200)
async def remove_task_note(note_id: int, db: Session = Depends(get_db)):
    db.query(TaskNote).filter_by(id=note_id).delete()
    db.commit()
    return ""
