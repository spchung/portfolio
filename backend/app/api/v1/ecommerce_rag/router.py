import asyncio
from typing import List
from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from .llm_handlers.open_ai_handler import OpenAIHandler
from app.api.v1.ecommerce_rag.context.context import ChatHistory, EcommerceRagContextManager
from .chat_handler import generate_streaming_response, get_context_snapshot, clear_context_snapshot

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from pydantic import BaseModel
class ChatRequestBody(BaseModel):
    message: str

@router.post("/chat")
async def stream(body: ChatRequestBody):
    user_query = body.message
    return StreamingResponse(
        generate_streaming_response(user_query), media_type="text/event-stream"
    )

@router.get("/context-snapshot")
async def context_snapshot(session_id: str):
    return await get_context_snapshot(session_id)

@router.delete("/clear-context-snapshot")
async def context_snapshot(session_id: str):
    return await clear_context_snapshot(session_id)

@router.get("/test-classifier")
async def product_review(msg: str, context:str=None):
    return OpenAIHandler().classify_query_v2(msg, context=context)

@router.post("/similar-recommendation")
async def product_review(product_ids:List[int], body: ChatRequestBody):
    pass