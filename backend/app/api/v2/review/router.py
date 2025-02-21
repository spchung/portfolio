from fastapi import HTTPException, APIRouter
from app.models.pg.sephora import SephoraReview
from app.db.postgres import SessionDepAsync, AsyncSession
from sqlalchemy.sql import text, select
from pydantic import BaseModel
from typing import List

router = APIRouter()
class BatchRequestBody(BaseModel):
    ids: List[str]

class BatchResponse(BaseModel):
    data: List[SephoraReview]
    meta_data: dict

@router.post("/batch")
async def stream(body: BatchRequestBody, session: SessionDepAsync) -> BatchResponse:
    prod_ids = body.ids

    res = await session.execute(
        select(SephoraReview).where(
            SephoraReview.review_id.in_(prod_ids)))
    
    reviews = res.scalars().all()
    
    return BatchResponse(data=reviews, meta_data={
        "total": len(reviews)
    })

@router.get("/<review_id>")
async def get_product(review_id: str, session: SessionDepAsync):
    res = await session.execute(select(SephoraReview).where(SephoraReview.review_id == review_id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Review not found")
    return product