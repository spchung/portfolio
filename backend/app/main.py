from fastapi import FastAPI, APIRouter
from app.api.v1.routes import router as api_v1_router
from app.db.postgres import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Portfolio",
    description="",
    version="0.0.1"
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific domains
    allow_credentials=True,  # Allows sending cookies and authentication headers
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_v1_router, prefix="/api/v1")

app.on_event("startup")(create_db_and_tables)