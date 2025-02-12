from fastapi import HTTPException, APIRouter
from app.db.postgres import SessionDep
from app.core.services.openai.chat import Chat
from app.middlewares.logging import log_around_execution

'''
Simple openAI chat wrapper 
'''

router = APIRouter()

chat_client = Chat(model="gpt-3.5-turbo")

@router.post("/")
@log_around_execution
async def chat(message: str):
    return chat_client.chat(message)