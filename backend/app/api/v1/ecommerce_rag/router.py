from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from collections import defaultdict
from typing import List
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from .llm_handlers.open_ai_handler import OpenAIHandler

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()
limit = 3

async def generate_streaming_response(user_query: str):
    metaData = defaultdict(str)
    
    handler = OpenAIHandler()
    queryLabel = handler.classify_query(user_query)

    metaData['intention'] = queryLabel

    if queryLabel == 'product_search':
        query, pgProducts = await handler.search_product_title(user_query, limit, metaData=metaData)
        response = handler.product_search_rewrite(query, pgProducts, stream=True, metaData=metaData)
    
    elif queryLabel == 'review_search':
        query, reviews, products = await handler.search_review(user_query, limit)
        response = handler.review_search_rewrite(query, reviews, products, stream=True)

    else:
       response = handler.create_completions(user_query, stream=True)

    totalResponseTokens = 0
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            totalResponseTokens += len(content.split())
            yield content
        await asyncio.sleep(0)
    

    metaData['tokens_used'] = totalResponseTokens
    
    # yield metadata
    yield f'event: metadata\ndata: {json.dumps(metaData)}\n\n'


async def fake_stream_response(user_input: str):
    """Simulate token streaming"""
    for word in ["Hello", "there!", "This", "is", "a", "streaming", "response."]:
        yield word + " "
        await asyncio.sleep(0.5)  # Simulating delay


# TODO:
'''
context tracker:
- keep track of products mentioned
- keep track of user queries
- keep track of category of products mentioned
'''


from pydantic import BaseModel
import json
class ChatRequestBody(BaseModel):
    message: str

@router.post("/chat")
async def stream(body: ChatRequestBody):
    user_query = body.message
    return StreamingResponse(generate_streaming_response(user_query), media_type="text/event-stream")

@router.post("/product_review")
async def product_review(product_ids: List[int], body: ChatRequestBody):
    user_query = body.message
    return StreamingResponse(fake_stream_response("test"), media_type="text/event-stream")

@router.post("/similar-recommendation")
async def product_review(product_ids:List[int], body: ChatRequestBody):
    pass