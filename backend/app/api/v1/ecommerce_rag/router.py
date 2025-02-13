import asyncio
from typing import List
from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from .llm_handlers.open_ai_handler import OpenAIHandler
from app.api.v1.ecommerce_rag.context.context import ChatHistory, EcommerceRagContextManager

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()
limit = 1
llmCtxMgr = EcommerceRagContextManager(session_id="test")

async def generate_streaming_response(user_query: str):    
    chaHistory = ChatHistory()
    handler = OpenAIHandler()
    
    llmCtxMgr.start_response()
    chaHistory.user_query = user_query

    queryLabel = handler.classify_query_v2(user_query)
    chaHistory.user_intent = queryLabel

    # metadata return
    products = None
    reviews = None

    if queryLabel == 'product_search':
        query, products = await handler.search_product_title(user_query, limit=1)
        response = handler.product_search_rewrite(query, products, stream=True)
    
    elif queryLabel == 'review_search':
        query, reviews, products = await handler.search_review(user_query, limit=5)
        response = handler.review_search_rewrite(query, reviews, products, stream=True)
    
    elif queryLabel == 'review_of_product':
        '''
        TODO:
        1. get last mentioned products (pg) from the context manager
        2. query reviews of the product (pg)
        3. prompt for rewrite
        '''
        response = handler.create_completions("Tell the user: 'This feature is not ready yet, sorry :('", stream=True)
    
    else:
       response = handler.create_completions(user_query, stream=True)

    totalResponseTokens = 0
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            totalResponseTokens += len(content)
            full_response += content
            yield content
        await asyncio.sleep(0)

    # log response
    chaHistory.response = full_response
    
    # log total token
    chaHistory.complete()

    # metadata register
    llmCtxMgr.end_response(token_count=totalResponseTokens)
    llmCtxMgr.add_chat_history(chaHistory)
    llmCtxMgr.metadata.last_query_intent = queryLabel
    llmCtxMgr.metadata.products = products
    llmCtxMgr.metadata.reviews = reviews

    # yield metadata
    yield f'event: metadata\ndata: {llmCtxMgr.metadata.serialize()}\n\n'


from pydantic import BaseModel
import json
class ChatRequestBody(BaseModel):
    message: str

@router.post("/chat")
async def stream(body: ChatRequestBody):
    user_query = body.message
    return StreamingResponse(generate_streaming_response(user_query), media_type="text/event-stream")

@router.get("/test-classifier")
async def product_review(msg: str, context:str=None):
    return OpenAIHandler().classify_query_v2(msg, context=context)

@router.post("/similar-recommendation")
async def product_review(product_ids:List[int], body: ChatRequestBody):
    pass