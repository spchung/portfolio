from pydantic import BaseModel
from fastapi import HTTPException, APIRouter
from app.api.v2.llm.chat.chat import chat
from fastapi.responses import StreamingResponse

router = APIRouter()

class ChatRequestBody(BaseModel):
    message: str

@router.post("/langchain-chat")
async def langchain_chat(body: ChatRequestBody, thread_id: str=None):
    '''
    Based on https://python.langchain.com/docs/tutorials/chatbot/
    '''
    return StreamingResponse(chat(body.message, thread_id), media_type="text/event-stream")