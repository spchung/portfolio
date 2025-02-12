# aggregate all routes

from fastapi import APIRouter
from .chat.router import router as chat_router
from app.api.v1.qa.router import router as qa_router
from app.api.v1.summary.router import router as summary_router
from app.api.v1.search.router import router as search_router
from app.api.v1.ecommerce_rag.router import router as rag_router


router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["chat"])
# router.include_router(qa_router, prefix="/qa", tags=["qa"])
# router.include_router(summary_router, prefix='/summary', tags=['summary'])
router.include_router(search_router, prefix='/search', tags=['search'])
router.include_router(rag_router, prefix='/ecommerce-rag', tags=['ecommerce-rag'])