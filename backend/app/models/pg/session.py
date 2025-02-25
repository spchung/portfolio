from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column

class Session(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    user_id: str
    chat_json: dict = Field(default_factory=dict, sa_column=Column(JSON)) # serialized representation of chat