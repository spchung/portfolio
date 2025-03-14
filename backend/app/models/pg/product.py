# sql model
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlalchemy import Text, JSON, Column
from app.models.milvus import MilvusSearchResultItem

# SQL Model
class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    parent_asin: str = Field(unique=True)
    title: str | None
    main_category: str | None
    average_rating: float | None
    store: str | None
    rating_number: int
    features: str = Field(sa_column=Text())
    description: str = Field(sa_column=Text())
    price: float | None
    images: list = Field(sa_column=Column(JSON), default_factory=list)
    categories: str = Field(sa_column=Text())
    details: dict = Field(sa_column=Column(JSON), default_factory=dict)
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))

    def list_to_text(self, data: list):
        return '\n'.join(data)

    @classmethod
    def from_dict(cls, data: dict):
        def list_to_text(data: list):
            return '\n'.join(data)
        
        return cls(
            parent_asin=data.get('parent_asin'),
            title=data.get('title'),
            main_category=data.get('main_category'),
            average_rating=data.get('average_rating'),
            store=data.get('store'),
            rating_number=data.get('rating_number'),
            features=list_to_text(data.get('features')),
            description=list_to_text(data.get('description')),
            price=data.get('price'),
            images=data.get('images'),
            categories=list_to_text(data.get('categories')),
            details=data.get('details'),
            meta=data.get('meta')
        )
    
    def to_dict(self):
        return self.model_dump()

    def to_mixed_model(self, milvusResult: MilvusSearchResultItem):
        return ProductMixedModel(
            product=self,
            milvus=milvusResult
        )

    def to_llm_context(self):
        context = f'Product: {self.title}\n Parent Asin: {self.parent_asin}\n'
        if self.features.strip(): 
            context += f"Features: {self.features.strip()}"
        if self.description.strip():
            context += f"Description: {self.description.strip()}"
        return context

# Milvius + SQL Model Mixed model for vector search results
class ProductMixedModel(BaseModel):
    product: Product
    milvus: MilvusSearchResultItem