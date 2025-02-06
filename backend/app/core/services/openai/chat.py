from pydantic import BaseModel
from typing import List, Dict

from openai import OpenAI
import dotenv
dotenv.load_dotenv()

client = OpenAI()

class Message(BaseModel):
    role: str
    content: str

class ContextManager:
    '''
    Simple context
    - saves last n messages
    '''
    def __init__(self, limit: int):
        self.history = []
        self.limit = limit
    
    def add_message(self, message: Message):
        self.history.append(message)
        if len(self.history) > self.limit:
            self.history.pop(0)

    def build_with_user_message(self, user_input: str):
        messages = []
        for historic_message in self.history:
            messages.append({"role": historic_message.role, "content": historic_message.content})
        messages.append({"role": "user", "content": user_input})
        return messages

class Chat:
    def __init__(self, model: str):
        self.model = model
        self.context_manager = ContextManager(limit=4)

    def chat(self, user_input: str):
        messages = self.context_manager.build_with_user_message(user_input)
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            user_message = Message(role="user", content=user_input)
            self.context_manager.add_message(user_message)
             
            response_message = Message(role="assistant", content=response.choices[0].message.content)
            self.context_manager.add_message(response_message)
            return response_message.content
        except Exception as e:
            return f"Error: {e}"