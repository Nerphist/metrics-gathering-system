from fastapi import APIRouter

__all__ = ['tasks_router', 'tasks']

tasks_router = APIRouter(
    prefix="/tasks",
    tags=['tasks']
)
