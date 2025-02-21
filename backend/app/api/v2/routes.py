# aggregate all routes

from fastapi import APIRouter
from app.api.v2.skincare_gpt.router import router as chat_router
from app.api.v2.product.router import router as product_router
from app.api.v2.review.router import router as review_router

router = APIRouter()
router.include_router(chat_router, prefix="/skincare-gpt", tags=["skincare-gpt"])
router.include_router(product_router, prefix="/product", tags=["product"])
router.include_router(review_router, prefix="/reveiw", tags=["reveiw"])