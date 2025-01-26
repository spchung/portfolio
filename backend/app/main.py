from fastapi import FastAPI, APIRouter
from app.api.v1.routes import router as api_v1_router

app = FastAPI(
    title="Portfolio",
    description="",
    version="0.0.1"
)

app.include_router(api_v1_router, prefix="/api/v1")