from fastapi import FastAPI

from api.routes import router

app = FastAPI(title="Market Data Intelligence Platform")
app.include_router(router)
