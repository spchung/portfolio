from fastapi import FastAPI, APIRouter
# from db import create_db_and_tables

main_router = APIRouter()

@main_router.get("/")
def root():
    return {"message": "Hello World"}

app = FastAPI(
    title="Your API",
    description="Your API Description",
    version="1.0.0"
)

app.include_router(main_router, prefix="/api/v1")


# ## start up event
# @app.on_event("startup")
# def on_startup():
#     print("Creating database and tables")
#     create_db_and_tables()