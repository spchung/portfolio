from pydantic import BaseModel
from typing import List
from datetime import datetime as dt
from app.models.pg.product import Product
from app.models.pg.review import Review
from openai import OpenAI
import json

import dotenv
dotenv.load_dotenv()

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

    def serialize(self):
        return self.model_dump_json()



## service
class RunningSummaryManager():
    def __init__(self, k: int = 3, windowSize: int = 5):
        self.k = k
        self.windowSize = windowSize
        self.llm = OpenAI()
        self.running_summary = None
    
    def generate(self, chatHistory: List[ChatHistory]):
        '''
        Generate a running summary of the conversation

        window_size = 5

        kChatHistory = [chat1, chat2, chat3, chat4, chat5, chat6, chat7, chat8, chat9, chat10]
        k = 3
        '''
        if len(chatHistory) <= self.k:
            return None

        turnsToSummarize = chatHistory[:-self.k]

        previousSummary = None
        if len(turnsToSummarize) > self.windowSize:
            turnsToSummarize = turnsToSummarize[-self.windowSize:]
            previousSummary = self.running_summary
        
        # prommpt for summary
        chatContext = ""
        for chat in turnsToSummarize:
            chatContext += f"User: {chat.user_query}\n"
        
        prompt = f"""
        Make a short summary what the user has been talking about below:

        {chatContext}

        Summary:
        """

        if previousSummary:
            prompt = f"""
            Make a short summary what the user has been talking about below while considering the previous summary:
            
            Previous Summary:
            {previousSummary}

            Conversation:
            {chatContext}

            Summary:
            """
        
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content.strip()
        self.running_summary = summary
        print(summary)
        return summary
    
    def __repr__(self):
        return self.running_summary
    
class SkincareGPTContextManager():
    def __init__(self, session_id: str, window_size: int = 5, k_chat_size: int = 3):
        self.session_id = session_id
        self.history = []
        self.window_size = window_size
        self.k_chat_size = k_chat_size
        self.metadata = MetaData()
        self.running_summary = None
        self.last_prompt = None
        self.running_summary_manager = RunningSummaryManager(k=k_chat_size, windowSize=window_size)
        self.product_ids = [] 
        self.review_ids = []

    def serialize(self):
        return json.dumps({
            "session_id": self.session_id,
            "history": [history.model_dump() for history in self.history],
            "metadata": self.metadata.model_dump(),
            "running_summary": self.running_summary,
            "last_prompt": self.last_prompt,
            "product_ids": self.product_ids,
            "review_ids": self.review_ids
        })
    
    ## metadata methods
    def start_response(self) -> None:
        self.metadata.last_query_start_time = dt.now().timestamp()
    
    def end_response(self, token_count: int) -> None:
        self.metadata.last_query_end_time = dt.now().timestamp()
        self.metadata.elapsed_seconds = self.metadata.last_query_end_time - self.metadata.last_query_start_time
        self.metadata.last_response_tokens = token_count

    def set_product_ids(self, product_ids: List[str]) -> None:
        self.product_ids = product_ids
    
    def set_reviews(self, review_ids: List[str]) -> None:
        self.review_ids = review_ids

    ## context methods
    def add_chat_history(self, chat_history: ChatHistory) -> None:
        if len(self.history) >= self.window_size:
            self.history.pop(0)
        self.history.append(chat_history)

        self.running_summary = self.running_summary_manager.generate(self.history)
    
    def to_llm_context(self, turns=None) -> str:
        if turns is None:
            turns = self.window_size

        context = []
        for chat in self.history[-turns:]:
            context.append(chat.user_query)
            context.append(chat.response)
        return "\n".join(context)