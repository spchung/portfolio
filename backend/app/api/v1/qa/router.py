from fastapi import HTTPException, APIRouter
from app.db.postgres import SessionDep
from app.core.services.huggingface.qa import StrictQaService, answer_question_with_no_answer

'''
HuggingFace Q&A with context
'''

router = APIRouter()


context = '''
Building agents with LLM (large language model) as its core controller is a cool concept. Several proof-of-concepts demos, such as AutoGPT, GPT-Engineer and BabyAGI, serve as inspiring examples. The potentiality of LLM extends beyond generating well-written copies, stories, essays and programs; it can be framed as a powerful general problem solver.
'''
strict_qa_service = StrictQaService()
@router.post("/strict-qa-answer")
def chat(message: str):
    answer, inline_attention = strict_qa_service.answer_question(message, context)
    return {"answer": answer, "inline_attention": inline_attention}


@router.post("/context-convo")
def chat(message: str):
    resp = answer_question_with_no_answer(message, context)
    return {"answer": resp}