from fastapi import HTTPException, APIRouter
from app.db.milvus import client
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.core.services.vector_search.query import MilvusCollectionService
from app.db.postgres import SessionDep, SessionDepAsync
# from app.models.pg.product import Product
from app.models.pg.review import Review
from sqlalchemy.sql import text, select

router = APIRouter()
collection_name = 'review'

@router.post("/review-title")
async def reviewTitleSearch(query: str, session: SessionDepAsync, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], anns_field="title_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        productIds = [item.id for item in milvusEnts]

        # query postgres
        rows = await session.execute(select(Review).filter(Review.id.in_(productIds)).order_by(Review.id))
        pgProducts = rows.scalars().all()

        # zip sorted results and product mixed models
        mixedModels = [pgProd.to_mixed_model(mProd) for mProd, pgProd in zip(milvusEnts, pgProducts)]
        return mixedModels
    
    except Exception as e:
        # raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def reviewSearch(query: str, session: SessionDepAsync, limit: int = 3):
    queryVec = create_embedding_1536(query)
    serv = MilvusCollectionService(collection_name)
    try:
        # query milvus
        milvusEnts = serv.query([queryVec], anns_field="review_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.id)
        reviewIds = [item.id for item in milvusEnts]

        # query postgres
        rows = await session.execute(select(Review).filter(Review.id.in_(reviewIds)).order_by(Review.id))
        pgReviews = rows.scalars().all()

        # zip sorted results and product mixed models
        mixedModels = [pgReview.to_mixed_model(mReview) for mReview, pgReview in zip(milvusEnts, pgReviews)]
        return mixedModels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))