from random import randrange

from fastapi import FastAPI
from starlette.responses import JSONResponse

from auth_api import get_user
from models import MetricsData

app = FastAPI()


@app.get("/dashboard-for-user/{user_id}/")
async def dashboard(user_id: int):
    user = get_user(user_id)
    if not user:
        return JSONResponse(content={'details': 'User does not exist'}, status_code=400)

    metrics = []
    for i in range(5):
        building = f'building{i}'
        for metric_type in ['heat', 'energy']:
            m = MetricsData(building=building, metric_type=metric_type, value=randrange(1000), unit='kJ')
            metrics.append(m.as_dict())
        m = MetricsData(building=building, metric_type='water', value=randrange(100), unit='m^3')
        metrics.append(m.as_dict())
    return JSONResponse(content={'metrics': metrics}, status_code=200)
