from fastapi import FastAPI, APIRouter
from app.api.v1.routes import router as api_v1_router
from app.db.postgres import create_db_and_tables

app = FastAPI(
    title="Portfolio",
    description="",
    version="0.0.1"
)

app.include_router(api_v1_router, prefix="/api/v1")

app.on_event("startup")(create_db_and_tables)