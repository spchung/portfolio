import json
from uuid import uuid4
from typing import List
from openai import OpenAI
from app.db.redis import r
from datetime import datetime as dt
from app.models.api.context import ChatHistory, MetaData, NamedEntity, UserPreferences

import dotenv
dotenv.load_dotenv()

class UserPerferenceManager:
    '''
    Manages user preferences
    - generate questions 
    - collect user information
    '''
    def __init__(self):
        self.attempted = False
        self.user_preferences = UserPreferences()

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
        return summary
    
    def __repr__(self):
        return self.running_summary

class SkincareGPTContext:
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
        self.named_entities = []
    
    @staticmethod
    def load(context_json: str):
        context_dict = json.loads(context_json)
        k_chat_size = context_dict['k_chat_size']
        window_size = context_dict['window_size']

        context = SkincareGPTContext(context_dict['session_id'], window_size, k_chat_size)
        context.history = [ChatHistory(**history) for history in context_dict['history']]
        context.metadata = MetaData(**context_dict['metadata'])
        context.running_summary = context_dict['running_summary']
        context.last_prompt = context_dict['last_prompt']
        context.product_ids = context_dict['product_ids']
        context.review_ids = context_dict['review_ids']
        context.named_entities = [NamedEntity(**entity) for entity in context_dict['named_entities']]
        return context
    
    def model_dump(self):
        return {
            "session_id": self.session_id,
            'window_size': self.window_size,
            'k_chat_size': self.k_chat_size,
            "history": [history.model_dump() for history in self.history],
            "metadata": self.metadata.model_dump(),
            "running_summary": self.running_summary,
            "last_prompt": self.last_prompt,
            "product_ids": self.product_ids,
            "review_ids": self.review_ids,
            'named_entities': [entity.model_dump() for entity in self.named_entities]
        }

    def serialize(self):
        return json.dumps({
            "session_id": self.session_id,
            'window_size': self.window_size,
            'k_chat_size': self.k_chat_size,
            "history": [history.model_dump() for history in self.history],
            "metadata": self.metadata.model_dump(),
            "running_summary": self.running_summary,
            "last_prompt": self.last_prompt,
            "product_ids": self.product_ids,
            "review_ids": self.review_ids,
            "named_entities": [entity.model_dump() for entity in self.named_entities]
        })
    
    ## metadata methods
    def start_response(self) -> None:
        self.metadata.last_query_start_time = dt.now().timestamp()
    
    def end_response(self, token_count: int) -> None:
        self.metadata.last_query_end_time = dt.now().timestamp()
        self.metadata.elapsed_seconds = self.metadata.last_query_end_time - self.metadata.last_query_start_time
        self.metadata.last_response_tokens = token_count

    ## NER methods
    def register_named_entities(self, entities: dict) -> None:
        lis = []
        for key, ent_lis in entities.items():
            for value in ent_lis:
                entity = NamedEntity(label=key, text=value)
                lis.append(entity)

        # if not exists, append
        for entity in lis:
            if entity not in self.named_entities:
                self.named_entities.append(entity)

    ## context methods
    def set_product_ids(self, product_ids: List[str]) -> None:
        self.product_ids = product_ids
    
    def set_reviews(self, review_ids: List[str]) -> None:
        self.review_ids = review_ids

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

class SkincareGPTContextManager:
    def __init__(self, limit = 3):
        self.pool = {} # session_id: SkincareGPTContext
        self.count = 0
        self.limit = limit
        self.ordered_keys = [] # List[session_id] ordered by last used - descending (-1 is the most recent)

    def generate_session_id(self) -> str:
        return str(uuid4())

    def register_activity(self, context: SkincareGPTContext) -> None:
        if context.session_id in self.pool:
            self.ordered_keys.remove(context.session_id)
            self.ordered_keys.append(context.session_id)
            return 
        
        if self.count >= self.limit:
            key = self.ordered_keys.pop(0)
            del self.pool[key]
            self.pool[context.session_id] = context
            self.ordered_keys.append(context.session_id)
        else:
            self.count += 1
            self.pool[context.session_id] = context
            self.ordered_keys.append(context.session_id)
        
    def remove_from_pool(self, context: SkincareGPTContext) -> None:
        del self.pool[context.session_id]
        self.ordered_keys.remove(context.session_id)
        self.count -= 1

    def get_context(self, session_id: str) -> SkincareGPTContext:
        if session_id in self.pool:
            context = self.pool[session_id]
            self.register_activity(context)
            return context

        context_json = r.get(session_id)
        if context_json:
            context = SkincareGPTContext.load(context_json)
        else:
            context = SkincareGPTContext(session_id)
        self.register_activity(context)
        return context