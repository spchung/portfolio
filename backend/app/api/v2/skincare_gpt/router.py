import asyncio
from typing import List
from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from app.api.v2.skincare_gpt.handlers.open_ai_handler import OpenAIHandler
'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from pydantic import BaseModel
class ChatRequestBody(BaseModel):
    message: str

async def generate_streaming_response(user_query: str):
    response = "hello there good sir, what can I do for you today?"
    for word in response.split(" "):
        yield f"data: {word}\n\n"
        await asyncio.sleep(1)


@router.post("/chat")
async def stream(body: ChatRequestBody):
    user_query = body.message
    return StreamingResponse(
        generate_streaming_response(user_query), media_type="text/event-stream"
    )

@router.post("/query_vector")
async def query_vector(body: ChatRequestBody):
    user_query = body.message
    return OpenAIHandler().query_vector(user_query)


# @router.get("/context-snapshot")
# async def context_snapshot(session_id: str):
#     return await get_context_snapshot(session_id)

# @router.delete("/clear-context-snapshot")
# async def context_snapshot(session_id: str):
#     return await clear_context_snapshot(session_id)

# @router.get("/test-classifier")
# async def product_review(msg: str, context:str=None):
#     return OpenAIHandler().classify_query_v2(msg, context=context)

# @router.post("/similar-recommendation")
# async def product_review(product_ids:List[int], body: ChatRequestBody):
#     pass