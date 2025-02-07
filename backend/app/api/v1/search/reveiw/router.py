from fastapi import HTTPException, APIRouter
from app.db.milvus import client
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.core.services.vector_search.query import MilvusCollectionService
from app.db.postgres import SessionDep
# from app.models.product import Product
from app.models.review import Review
from sqlalchemy.sql import text

router = APIRouter()
collection_name = 'review'

@router.post("/review-title")
def reviewTitleSearch(query: str, session: SessionDep, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [str(item.id) for item in milvusEnts]

        # query postgres
        q = f"SELECT * FROM review WHERE id IN ({','.join(productIds)}) order by id"
        rows = session.exec(text(q)).all()
        pgProducts = [Review(**dict(row._mapping)) for row in rows]

        # zip sorted results and product mixed models
        mixedModels = [pgProd.to_mixed_model(mProd) for mProd, pgProd in zip(milvusEnts, pgProducts)]
        return mixedModels
    
    except Exception as e:
        # raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
def reviewSearch(query: str, session: SessionDep, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], anns_field="review_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [str(item.id) for item in milvusEnts]

        # query postgres
        q = f"SELECT * FROM review WHERE id IN ({','.join(productIds)}) order by id"
        rows = session.exec(text(q)).all()
        pgReviews = [Review(**dict(row._mapping)) for row in rows]

        # zip sorted results and product mixed models
        mixedModels = [pgReview.to_mixed_model(mReview) for mReview, pgReview in zip(milvusEnts, pgReviews)]
        return mixedModels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        # raise e 