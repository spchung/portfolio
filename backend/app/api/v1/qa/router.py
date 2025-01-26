from fastapi import HTTPException, APIRouter
from app.db.database import SessionDep
from app.services.huggingface.qa import QaService

'''
HuggingFace Q&A with context
'''

router = APIRouter()


context = "Alpha is the name of my dog."
qa_service = QaService()
@router.post("/answer")
def chat(message: str):
    return qa_service.answer_question(message, context)