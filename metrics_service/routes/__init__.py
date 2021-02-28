from fastapi import APIRouter

__all__ = ['metrics_router', 'location', 'metrics']

metrics_router = APIRouter(
    prefix="/metrics",
    tags=['metrics']
)
