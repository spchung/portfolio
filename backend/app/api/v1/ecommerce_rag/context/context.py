from pydantic import BaseModel
from typing import List
from datetime import datetime as dt
from app.models.product import Product
from app.models.review import Review

class ChatHistory(BaseModel):
    user_query: str | None = None
    response: str | None = None
    user_intent: str | None = None
    topic: str | None = None # could be product name, or category name
    timestamp: float | None = None
    struct_data: dict | None = None # for any structured data as additional context

    def serialize(self):
        return self.model_dump_json()
    
    def complete(self):
        self.timestamp = dt.now().timestamp()
    

class MetaData(BaseModel):
    last_response_tokens: int = 0
    last_query_start_time: float | None = None
    last_query_end_time: float | None = None
    elapsed_seconds: float = 0
    last_query_intent: str | None = None
    products: List[Product] | None = None
    reviews: List[Review] | None = None

    def serialize(self):
        return self.model_dump_json()


class EcommerceRagContextManager(BaseModel):
    session_id: str
    history: List[ChatHistory] = []
    window_size: int = 5 # how many ChatHistory object to keep track
    metadata: MetaData = MetaData()

    def serialize(self):
        return self.model_dump_json()
    
    ## metadata methods
    def start_response(self) -> None:
        self.metadata.last_query_start_time = dt.now().timestamp()
    
    def end_response(self, token_count: int) -> None:
        self.metadata.last_query_end_time = dt.now().timestamp()
        self.metadata.elapsed_seconds = self.metadata.last_query_end_time - self.metadata.last_query_start_time
        self.metadata.last_response_tokens = token_count

    ## context methods
    def add_chat_history(self, chat_history: ChatHistory) -> None:
        if len(self.history) >= self.window_size:
            self.history.pop(0)
        self.history.append(chat_history)
    
    def to_llm_context(self, turns=None) -> str:
        if turns is None:
            turns = self.window_size

        context = []
        for chat in self.history[-turns:]:
            context.append(chat.user_query)
            context.append(chat.response)
        return "\n".join(context)

