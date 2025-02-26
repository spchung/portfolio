from sqlmodel import SQLModel, Field
from sqlalchemy import Text, JSON, Column

class Metadata(SQLModel, table=True):
    id : int = Field(default=None, primary_key=True)
    group: str
    key : str
    values: list = Field(sa_column=Column(JSON), default_factory=list)
    