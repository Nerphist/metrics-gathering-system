from datetime import datetime
from typing import List

from pydantic import validator, Field
from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from auth_api import get_user
from models.tasks import Task, TaskNote

TaskNoteModel = sqlalchemy_to_pydantic(TaskNote)


class TaskModel(sqlalchemy_to_pydantic(Task)):
    notes: List[TaskNoteModel]


class AddTaskModel(BaseModel):
    creator_id: int
    name: str
    priority: int = None
    due_date: datetime = Field(default_factory=datetime.now)
    completion_date: datetime = Field(default_factory=datetime.now)
    description: str = None
    status: str = 'To do'
    grade: float = None
    assignee_id: int = None

    @validator('assignee_id', 'creator_id')
    def user_exists(cls, value):
        if value is not None and not get_user(value):
            raise ValueError(f'Wrong user id: {value}')
        return value


class AddTaskNoteModel(BaseModel):
    user_id: int
    task_id: int
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
