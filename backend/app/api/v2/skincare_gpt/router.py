from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from app.api.v2.skincare_gpt.handlers.chat_handler import ChatHandler, context_manager

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from pydantic import BaseModel
class ChatRequestBody(BaseModel):
    message: str
    session_id: str

@router.post("/chat")
async def stream(body: ChatRequestBody):
    session_id = body.session_id
    handler = ChatHandler(session_id)
    user_query = body.message
    return StreamingResponse(
        handler.chat(
            user_query, 
        ), 
        media_type="text/event-stream"
    )

@router.get("/new-session")
async def new_session():
    '''
    Register a new session and set the session_id in browser cookies
    '''
    session_id = context_manager.generate_session_id()
    context = context_manager.get_context(session_id)
    context_manager.register_activity(context)
    return {"session_id": session_id}

@router.get("/context-snapshot")
def context_snapshot(session_id: str):
    context = context_manager.get_context(session_id)
    return context.model_dump()

@router.get("/last-prompt")
def last_prompt(session_id: str):
    handler = OpenAIHandler(session_id)
    return handler.get_last_prompt()

@router.post("/paraphrase")
def paraphrase(request: ChatRequestBody):
    handler = OpenAIHandler(request.session_id)
    res = handler.intent_classifier.skin_type(request.message)
    return res