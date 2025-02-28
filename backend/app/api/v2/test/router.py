from fastapi import APIRouter
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
    d = rule_based_tag(request.message)
    return d