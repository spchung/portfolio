from fastapi import HTTPException, APIRouter
from app.db.database import SessionDep
from app.services.openai.chat import Chat
'''
Simple openAI chat wrapper 
'''

router = APIRouter()

chat_client = Chat(model="gpt-4o")


@router.post("/")
def chat(message: str):
    return chat_client.chat(message)