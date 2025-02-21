from fastapi import HTTPException, APIRouter
from app.models.pg.sephora import SephoraProduct
from app.db.postgres import SessionDepAsync, AsyncSession
from sqlalchemy.sql import text, select
from pydantic import BaseModel
from typing import List

router = APIRouter()
class BatchRequestBody(BaseModel):
    ids: List[str]

class BatchResponse(BaseModel):
    data: List[SephoraProduct]
    meta_data: dict

@router.post("/batch")
async def stream(body: BatchRequestBody, session: SessionDepAsync) -> BatchResponse:
    prod_ids = body.ids

    res = await session.execute(
        select(SephoraProduct).where(
            SephoraProduct.product_id.in_(prod_ids)))
    
    products = res.scalars().all()
    
    return BatchResponse(data=products, meta_data={
        "total": len(products)
    })

@router.get("/<product_id>")
async def get_product(product_id: str, session: SessionDepAsync):
    res = await session.execute(select(SephoraProduct).where(SephoraProduct.product_id == product_id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product