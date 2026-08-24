from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from db import pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True)
    yield
    pool.close()


app = FastAPI(title="Market Data Intelligence Platform", lifespan=lifespan)
app.include_router(router)
