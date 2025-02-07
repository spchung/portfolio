from fastapi import APIRouter
from app.api.v1.search.product.router import router as product_router
from app.api.v1.search.reveiw.router import router as reveiw_router

router = APIRouter()
router.include_router(product_router, prefix='/product')
router.include_router(reveiw_router, prefix='/review')
