from pydantic import BaseModel
from typing import List
from base import BasePoint

# Product Payload Base model
class BaseProductPointPayload(BaseModel):
    product_id: str
    price_usd: float

    size: str | None
    primary_category: str | None
    secondary_category: str | None
    tertiary_category: str | None
    rating: float | None
    reviews: int | None
    brand_name: str | None

# POINT - product_name
class ProductNamePointPayload(BaseProductPointPayload):
    entity_type: str = 'product'
    vector_column: str = 'product_name'

    @classmethod
    def from_dict(cls, data:dict):
        def empty_string_to_none(val):
            return None if val == '' else val

        return ProductNamePointPayload(
            product_id=data.get('product_id'),
            price_usd=data.get('price_usd'),
            size=data.get('size'),
            primary_category=data.get('primary_category'),
            secondary_category=data.get('secondary_category'),
            tertiary_category=data.get('tertiary_category'),
            rating=empty_string_to_none(data.get('rating')),
            reviews=empty_string_to_none(data.get('reviews')),
            brand_name=data.get('brand_name')
        )

class ProductNamePoint(BasePoint):
    payload: ProductNamePointPayload

# POINT - product_ingredients
class ProductIngredientsPointPayload(BaseProductPointPayload):
    entity_type: str = 'product'
    vector_column: str = 'product_ingredients'

    @classmethod
    def from_dict(cls, data:dict):
        def empty_string_to_none(val):
            return None if val == '' else val

        return ProductIngredientsPointPayload(
            product_id=data.get('product_id'),
            price_usd=data.get('price_usd'),
            size=data.get('size'),
            primary_category=data.get('primary_category'),
            secondary_category=data.get('secondary_category'),
            tertiary_category=data.get('tertiary_category'),
            rating=empty_string_to_none(data.get('rating')),
            reviews=empty_string_to_none(data.get('reviews')),
            brand_name=data.get('brand_name')
        )
        

class ProductIngredientsPoint(BasePoint):
    payload: ProductIngredientsPointPayload

# POINT - product_highlights
class ProductHighlightsPointPayload(BaseProductPointPayload):
    entity_type: str = 'product'
    vector_column: str = 'product_highlights'

    @classmethod
    def from_dict(cls, data:dict):
        def empty_string_to_none(val):
            return None if val == '' else val

        return ProductHighlightsPointPayload(
            product_id=data.get('product_id'),
            price_usd=data.get('price_usd'),
            size=data.get('size'),
            primary_category=data.get('primary_category'),
            secondary_category=data.get('secondary_category'),
            tertiary_category=data.get('tertiary_category'),
            rating=empty_string_to_none(data.get('rating')),
            reviews=empty_string_to_none(data.get('reviews')),
            brand_name=data.get('brand_name')
        )

class ProductHighlightsPoint(BasePoint):
    payload: ProductHighlightsPointPayload

