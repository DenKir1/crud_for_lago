from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from app.config.settings import settings
from app.handlers.lago import lago_crud_router
from app.utils.lago import get_or_create_plan, delete_plan, get_or_create_billable_metric, delete_metric


@asynccontextmanager
async def lifespan(app: FastAPI):
    metric = get_or_create_billable_metric()
    plan = get_or_create_plan(name_code=settings.app.PLAN_CODE,
                              billable_id=metric.lago_id,
                              billable_code=metric.code)
    yield
    delete_plan(plan)
    delete_metric(metric)


app = FastAPI(lifespan=lifespan)


app.include_router(lago_crud_router)


if __name__ == "__main__":
    if not settings.app.IS_PROD:
        uvicorn.run(app, host="127.0.0.1", port=8000)
