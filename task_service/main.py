import uvicorn
from fastapi import FastAPI

from middlewares.auth_middleware import AuthMiddleware
from routes import *

app = FastAPI()
app.include_router(tasks_router)
app.add_middleware(AuthMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8003, log_level="info")
