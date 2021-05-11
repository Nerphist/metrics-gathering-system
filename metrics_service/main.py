import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from middlewares.auth_middleware import AuthMiddleware
from routes import metrics_router
from routes.metrics import *
from routes.locations import *

app = FastAPI()
app.include_router(metrics_router)
app.add_middleware(AuthMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8002, log_level="info")
