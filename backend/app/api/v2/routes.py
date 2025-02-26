# aggregate all routes

from fastapi import APIRouter
from app.api.v2.skincare_gpt.router import router as chat_router
from app.api.v2.product.router import router as product_router
from app.api.v2.review.router import router as review_router
from app.api.v2.llm.router import router as llm_router
from app.api.v2.test.router import router as test_router

router = APIRouter()
router.include_router(chat_router, prefix="/skincare-gpt", tags=["skincare-gpt"])
router.include_router(product_router, prefix="/product", tags=["product"])
router.include_router(review_router, prefix="/review", tags=["review"])
router.include_router(llm_router, prefix="/llm", tags=["llm"])
router.include_router(test_router, prefix="/test", tags=["test"])