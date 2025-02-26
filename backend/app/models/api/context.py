from pydantic import BaseModel
from typing import List
from datetime import datetime as dt

class MetaData(BaseModel):
    last_response_tokens: int = 0
    last_query_start_time: float | None = None
    last_query_end_time: float | None = None
    elapsed_seconds: float = 0
    last_query_intent: str | None = None

class ChatHistory(BaseModel):
    user_query: str | None = None
    response: str | None = None
    user_intent: str | None = None
    topic: str | None = None # could be product name, or category name
    timestamp: float | None = None
    struct_data: dict | None = None # for any structured data as additional context
    
    def complete(self):
        self.timestamp = dt.now().timestamp()

class UserPreferences(BaseModel):
    skin_type: str | None = None
    concerns: List[str] | None = None

class NamedEntity(BaseModel):
    label: str
    text: str

class RedisSessionModel(BaseModel):
    session_id: str
    history: List[dict] = []
    metadate: MetaData = MetaData()
    # topics: List[Topics] = []
    # user_preferences: UserPreferences = UserPreferences()