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
from app.db.postgres import SessionDep
from app.models.product import Product
from sqlalchemy.sql import text

router = APIRouter()

'''
vector search by title
'''

collection_name="product_title"

@router.post("/title")
def titleSearch(query: str, session: SessionDep, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [str(item.id) for item in milvusEnts]
        
        # query postgres
        q = f"SELECT * FROM product WHERE id IN ({','.join(productIds)}) order by id"
        rows = session.exec(text(q)).all()
        pgProducts = [Product(**dict(row._mapping)) for row in rows]

        # zip sorted results and product mixed models
        mixedModels = [pgProd.to_mixed_model(mProd) for mProd, pgProd in zip(milvusEnts, pgProducts)]
        return mixedModels
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
