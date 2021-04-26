from fastapi import APIRouter

__all__ = ['metrics_router', 'location_view', 'metrics_view']

metrics_router = APIRouter(
    prefix="/metrics",
    tags=['metrics']
)
