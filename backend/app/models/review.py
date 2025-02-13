# sql model
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlalchemy import Text, JSON, Column, DateTime
from sqlalchemy import BigInteger
from app.models.milvus import MilvusSearchResultItem

class Review(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str | None
    text: str | None = Field(sa_column=Text())
    images: list = Field(sa_column=Column(JSON), default_factory=list)
    asin: str | None
    parent_asin: str | None
    user_id: str | None
    timestamp: str | None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def to_dict(self):
        return self.model_dump()
    
    def to_mixed_model(self, milvusResult: MilvusSearchResultItem):
        return ReviewMixedModel(
            review=self,
            milvus=milvusResult
        )

    def to_llm_context(self):
        context = f'Title: {self.title}\nParent Asin: {self.parent_asin}\n'
        if self.text.strip(): 
            context += f"Review: {self.text.strip()}"
        return context

# Milvius + SQL Model Mixed model for vector search results
class ReviewMixedModel(BaseModel):
    review: Review
    milvus: MilvusSearchResultItem