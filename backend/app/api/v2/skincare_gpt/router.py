from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from app.api.v2.skincare_gpt.handlers.chat_handler import ChatHandler, context_manager
from app.api.v2.skincare_gpt.services.context_service import ContextService

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

@router.put("/reset-context")
def reset_context(session_id: str):
    return ContextService().reset_context(session_id)

@router.post("/recommend")
def context_snapshot(body: ChatRequestBody):
    session_id = body.session_id
    query = body.message
    context = context_manager.get_context(session_id)
    handler = ChatHandler(session_id)
    handler.recommend(query)
    return context.recommend()

@router.post("/ner")
def ner(body: ChatRequestBody):
    session_id = body.session_id
    query = body.message
    handler = ChatHandler(session_id)
    res = handler.ner_service.extract_entities(query)
    return res

@router.post("/intent")
async def recommendation(body: ChatRequestBody):
    session_id = body.session_id
    query = body.message
    handler = ChatHandler(session_id)
    intent, _ = handler.multi_calssifier.intent(query)
    return {"intent": intent.value}
