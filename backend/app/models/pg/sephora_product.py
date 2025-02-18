from pydantic import BaseModel
from typing import List

class SephoraProduct(BaseModel):
    product_id: str #0
    product_name: str #1
    brand_id: int #2
    brand_name: str #3
    loves_count: int #4
    rating: float #5
    reviews: int #6
    size: str | None #7
    ingredients: List[str] | None #11
    price_usd: int #12
    highlights: List[str] | None #20
    primary_category: str #21
    secondary_category: str | None #22
    teritary_category: str | None #23
