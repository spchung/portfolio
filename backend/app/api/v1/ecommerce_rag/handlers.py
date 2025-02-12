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
from .llm_rewrite import product_search_rewrite, review_search_rewrite

dotenv.load_dotenv()
client = OpenAI()

async def search_product_title(query: str, limit:int):
    collection = 'product_title'
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection)
    milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
    milvusEnts.sort(key=lambda x: x.id)
    productIds = [item.id for item in milvusEnts]

    # query pg
    pgProducts = []
    # Query PostgreSQL using SQLAlchemy ORM
    async with AsyncSession(asyncEngine) as session:
        result = await session.execute(select(Product).filter(Product.id.in_(productIds)).order_by(Product.id))
        pgProducts = result.scalars().all()
    
    # send to llm for rewrite
    return await product_search_rewrite(query, pgProducts, stream=True)

async def search_review(query:str, limit:int):
    collection = 'review'
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection)
    milvusEnts = serv.query([queryVec], anns_field="review_vector", limit=limit)
    milvusEnts.sort(key=lambda x: x.id)
    reviewIds = [str(item.id) for item in milvusEnts]

    # query pg - get reviews and Products
    pgReviews = []
    with Session(engine) as sess:
        # get top reveiw parent_asins
        q = f'SELECT parent_asin FROM review WHERE id IN ({",".join(reviewIds)}) order by id'
        sess.get(bind)
        rows = sess.exec(text(q)).all()
        parentAsins = [row[0] for row in rows]

        # get products
        if parentAsins:
            q = f"SELECT * FROM product WHERE parent_asin IN ({','.join(parentAsins)}) order by id"
            rows = sess.exec(text(q)).all()
            pgReviews = [Review(**dict(row._mapping)) for row in rows]

        else:
            # no products found
            pass


        

    return await review_search_rewrite(query, reviewIds, stream=True)