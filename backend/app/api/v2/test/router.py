from fastapi import HTTPException, APIRouter, Response
from fastapi.responses import StreamingResponse
from fastapi import Cookie
import json
from typing import Annotated
from app.api.v2.skincare_gpt.handlers.open_ai_handler import OpenAIHandler, context_manager
from app.core.ner_topic_extract.rule_based.rule_based_ner import rule_based_tag

'''
Ecommerce Rag Entry Point
'''

router = APIRouter()

from pydantic import BaseModel
class ChatRequestBody(BaseModel):
    message: str

@router.post("/")
def test_fuzzy(request: ChatRequestBody):
    """
    Test fuzzy search
    """
    _, d = rule_based_tag(request.message)
    return d