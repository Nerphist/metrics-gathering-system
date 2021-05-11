from fastapi import APIRouter

metrics_router = APIRouter(
    prefix="/metrics",
    tags=['metrics']
)
