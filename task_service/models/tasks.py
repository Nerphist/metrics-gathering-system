from datetime import datetime

from sqlalchemy import Column, String, UniqueConstraint, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class TaskNote(Base):
    __tablename__ = 'task_notes'

    user_id = Column(Integer, nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))


class Task(Base):
    __tablename__ = 'tasks'

    creator_id = Column(Integer, nullable=False, index=True)
    assignee_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    priority = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(255), nullable=False, default='To do')
    grade = Column(Float, nullable=True)
    due_date = Column(DateTime, nullable=False, default=datetime.now)
    completion_date = Column(DateTime, nullable=False, default=datetime.now)

    notes = relationship(TaskNote, backref='task')

    __tableargs__ = (
        UniqueConstraint('creator_id', 'assignee_id', 'name', name='_task_names_uc'),
        UniqueConstraint('creator_id', 'assignee_id', 'priority', name='_task_priorities_uc'),
    )
