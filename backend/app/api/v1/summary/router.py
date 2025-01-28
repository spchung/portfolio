from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from transformers import pipeline
from app.middlewares.logging import log_around_execution


class SummaryRequest(BaseModel):
    text: str

router = APIRouter()

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
@router.post("/summarize")
@log_around_execution
# add request: Request to allow middleware to log the request
async def summary(request: Request, summary_request: SummaryRequest, max_length: int = 130):
    summary = summarizer(summary_request.text, max_length=max_length, min_length=40, do_sample=False)
    return summary[0]['summary_text']