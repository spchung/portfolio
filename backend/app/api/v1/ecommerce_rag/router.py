from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from app.core.services.huggingface.qa import StrictQaService, answer_question_with_no_answer
import asyncio
from typing import List

from openai import OpenAI
import dotenv
dotenv.load_dotenv()

client = OpenAI()

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from app.core.ecommerce_rag.query_classifier import RetailIntentClassifier
from app.core.services.vector_search.query import MilvusCollectionService
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from sqlmodel import Session
from app.db.postgres import engine
from sqlalchemy.sql import text
from app.models.product import Product
from app.core.ecommerce_rag.context_aware_response import product_query_response

classifier = RetailIntentClassifier()
limit = 3

async def generate_streaming_response(user_query):
    query_label = classifier.classify(user_query)
    if query_label == 'product_search':
        # 1. query milvus
        collection = 'product_title'
        queryVec = create_embedding_1536(user_query)
        serv = MilvusCollectionService(collection)
        milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [str(item.id) for item in milvusEnts]

        # query pg
        pgProducts = []
        with Session(engine) as sess:
            q = f"SELECT * FROM product WHERE id IN ({','.join(productIds)}) order by id"
            rows = sess.exec(text(q)).all()
            pgProducts = [Product(**dict(row._mapping)) for row in rows]
        
        # send to llm for rewrite
        response = await product_query_response(user_query, pgProducts, stream=True)

    elif query_label == 'review_search':
        collection = 'review'
        queryVec = create_embedding_1536(user_query)
        
        yield "review wip"
    else:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": user_query}],
            stream=True  # Enable streaming
        ) 

    # stream response
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
        await asyncio.sleep(0)


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