import os
from sqlalchemy import create_engine
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}/{db_name}"
ASYNC_SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session_async() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session  # Yielding an async session

SessionDepAsync = Annotated[AsyncSession, Depends(get_session_async)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

async def dispose():
    await async_engine.dispose()