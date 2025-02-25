from fastapi import HTTPException, APIRouter, Response
from fastapi.responses import StreamingResponse
from fastapi import Cookie
from typing import Annotated
from app.api.v2.skincare_gpt.handlers.open_ai_handler import OpenAIHandler, context_manager
'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from pydantic import BaseModel
class ChatRequestBody(BaseModel):
    message: str

@router.post("/chat")
async def stream(body: ChatRequestBody, session_id: Annotated[str | None, Cookie()] = None):
    handler = OpenAIHandler(session_id)
    user_query = body.message
    return StreamingResponse(
        handler.chat(
            user_query, 
            session_id=session_id
        ), 
        media_type="text/event-stream"
    )

@router.get("/register-new-session")
async def register_new_session(response: Response):
    '''
    Register a new session and set the session_id in browser cookies
    '''
    session_id = context_manager.generate_session_id()
    response.set_cookie(
        key="session_id", 
        value=session_id,
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=60*60*24*7
    )
    return {"session_id": session_id}

@router.get("/context-snapshot")
def context_snapshot(session_id: str):
    handler = OpenAIHandler(session_id)
    return handler.get_context_snapshot()

@router.get("/last-prompt")
def last_prompt(session_id: str):
    handler = OpenAIHandler(session_id)
    return handler.get_last_prompt()