import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)