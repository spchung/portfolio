'''
RAG - Product search

Query behaviour - Hybrid:
Step 1: keyword parse
    - parse keywords used in direct query againt the database. e.g. 'laptop', 'price' ... etc
Step 2:
    - fuzzy vector search using description of needs. e.g. "good for student", "suitable for childdren" ... etc
'''
from fastapi import HTTPException, APIRouter
from app.db.milvus import client
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.core.services.vector_search.query import MilvusCollectionService
from app.db.postgres import SessionDepAsync, AsyncSession
from app.models.product import Product
from sqlalchemy.sql import text, select
from typing import List

router = APIRouter()

'''
vector search by title
'''
collection_name="product_title"

@router.post("/title")
async def titleSearch(query: str, session: SessionDepAsync, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [item.id for item in milvusEnts]
        
        # query postgres
        rows = await session.execute(select(Product).filter(Product.id.in_(productIds)).order_by(Product.id))
        pgProducts = rows.scalars().all()

        # zip sorted results and product mixed models
        mixedModels = [pgProd.to_mixed_model(mProd) for mProd, pgProd in zip(milvusEnts, pgProducts)]
        return mixedModels
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
