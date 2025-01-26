# aggregate all routes

from fastapi import APIRouter
from .chat.router import router as chat_router
from app.api.v1.qa.router import router as api_v1_qa_router


router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(api_v1_qa_router, prefix="/qa", tags=["qa"])