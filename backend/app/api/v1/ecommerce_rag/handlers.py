import asyncio
import dotenv
from openai import OpenAI
from app.core.services.vector_search.query import MilvusCollectionService
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import engine, asyncEngine
from sqlalchemy.sql import text
from app.models.product import Product
from app.models.review import Review
from typing import Tuple, List
from .llm_rewrite import product_search_rewrite, review_search_rewrite

dotenv.load_dotenv()
client = OpenAI()

async def search_product_title(query: str, limit:int, metaData={}) -> Tuple[str, List[Product]]:
    collection = 'product_title'
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection)
    milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
    milvusEnts.sort(key=lambda x: x.distance)
    productIds = [item.id for item in milvusEnts]

    # query pg
    pgProducts = []
    # Query PostgreSQL using SQLAlchemy ORM
    async with AsyncSession(asyncEngine) as session:
        result = await session.execute(select(Product).filter(Product.id.in_(productIds)).order_by(Product.id))
        pgProducts = result.scalars().all()

    return query, pgProducts

async def search_review(query:str, limit:int) -> Tuple[str, List[Review], List[Product]]:
    collection = 'review'
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection)
    milvusEnts = serv.query([queryVec], anns_field="review_vector", limit=limit)
    milvusEnts.sort(key=lambda x: x.distance)
    reviewIds = [item.id for item in milvusEnts]

    # query pg - get reviews and Products
    async with AsyncSession(asyncEngine) as session:
        # get top reveiw parent_asins
        reviews = await session.execute(
            select(Review).filter(Review.id.in_(reviewIds)).order_by(Review.id))
        reviews = reviews.scalars().all()
        
        parentAsins = [r.parent_asin for r in reviews]
        products = await session.execute(
            select(Product).filter(Product.parent_asin.in_(parentAsins)).order_by(Product.id))
        products = products.scalars().all()
    
    return query, reviews, products

    # return await review_search_rewrite(query, reviews, products, stream=True)