from sqlmodel import SQLModel, Field
from sqlalchemy import Text, JSON, Column
from typing import List, Optional
import json

class SephoraProduct(SQLModel, table=True):
    __tablename__ = 'sephora_product'
    product_id: str = Field(primary_key=True)
    product_name: str
    brand_id: int
    brand_name: str
    loves_count: int | None
    rating: float | None
    reviews: int | None
    size: Optional[str] = None
    ingredients: list =  Field(sa_column=Column(JSON), default_factory=list)
    price_usd: float
    highlights: list = Field(sa_column=Column(JSON), default_factory=list)
    primary_category: str
    secondary_category: Optional[str] = None
    teritary_category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        def text_lis_to_list(text):
            if not text:
                return []
            try:
                return json.loads(text.replace("'", '"'))
            except json.JSONDecodeError:
                return []
        
        def empty_to_none(value):
            if value == '':
                return None
            return value

        return SephoraProduct(
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            brand_id=data.get('brand_id'),
            brand_name=data.get('brand_name'),
            loves_count=empty_to_none(data.get('loves_count')),
            rating=empty_to_none(data.get('rating')),
            reviews=empty_to_none(data.get('reviews')),
            size=data.get('size'),
            ingredients=text_lis_to_list(data.get('ingredients', '[]')),
            price_usd=data.get('price_usd'),
            highlights=text_lis_to_list(data.get('highlights', '[]')),
            primary_category=data.get('primary_category'),
            secondary_category=data.get('secondary_category'),
            teritary_category=data.get('teritary_category')
        )

class SephoraReview(SQLModel, table=True):
    __tablename__ = 'sephora_review'
    review_id: str = Field(primary_key=True) ##
    author_id: str
    rating: int
    is_recommended: bool ##
    helpfulness: float | None
    total_feedback_count: int
    total_neg_feedback_count: int
    total_pos_feedback_count: int
    submission_time: str
    review_text: str = Field(sa_column=Text())
    review_title: str
    skin_tone: str | None
    eye_color: str | None
    skin_type: str | None
    hair_color: str | None
    product_id: str
    product_name: str
    brand_name: str
    price_usd: float

    @classmethod
    def from_dict(cls, data: dict):
        def empty_to_none(value):
            if value == '':
                return None
            return value

        def float_to_bool(value):
            return value == 1.0
        
        def empty_to_none(value):
            if value == '':
                return None
            return value
        
        return SephoraReview(
            review_id=data.get('review_id'),
            author_id=data.get('author_id'),
            rating=data.get('rating'),
            is_recommended=float_to_bool(data.get('is_recommended')),
            helpfulness=empty_to_none(data.get('helpfulness')),
            total_feedback_count=data.get('total_feedback_count'),
            total_neg_feedback_count=data.get('total_neg_feedback_count'),
            total_pos_feedback_count=data.get('total_pos_feedback_count'),
            submission_time=data.get('submission_time'),
            review_text=data.get('review_text'),
            review_title=data.get('review_title'),
            skin_tone=empty_to_none(data.get('skin_tone')),
            eye_color=empty_to_none(data.get('eye_color')),
            skin_type=empty_to_none(data.get('skin_type')),
            hair_color=empty_to_none(data.get('hair_color')),
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            brand_name=data.get('brand_name'),
            price_usd=data.get('price_usd')
        )
