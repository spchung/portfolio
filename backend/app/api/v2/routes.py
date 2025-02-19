# aggregate all routes

from fastapi import APIRouter
from app.api.v2.skincare_gpt.router import router as chat_router

router = APIRouter()
router.include_router(chat_router, prefix="/skincare-gpt", tags=["skincare-gpt"])