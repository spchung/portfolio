from pydantic import BaseModel
from base import BasePoint

# POINT - Review
class ReviewPointPayload(BaseModel):
    entity_type: str = 'review'
    vector_column: str = 'review_text'
    product_id: str
    price_usd: float

    rating: float | None
    is_recommended: bool | None
    review_title: str | None
    skin_tone: str | None
    eye_color: str | None
    skin_type: str | None
    hair_color: str | None
    product_name: str | None
    brand_name: str | None

    @classmethod
    def from_dict(cls, data:dict):
        def empty_string_to_none(val):
            return None if val == '' else val
        
        def check_bool(val):
            return val == '1.0'

        return ReviewPointPayload(
            product_id=data.get('product_id'),
            price_usd=data.get('price_usd'),
            rating=empty_string_to_none(data.get('rating')),
            is_recommended=check_bool(data.get('is_recommended')),
            review_title=empty_string_to_none(data.get('review_title')),
            skin_tone=empty_string_to_none(data.get('skin_tone')),
            eye_color=empty_string_to_none(data.get('eye_color')),
            skin_type=empty_string_to_none(data.get('skin_type')),
            hair_color=empty_string_to_none(data.get('hair_color')),
            product_name=empty_string_to_none(data.get('product_name')),
            brand_name=empty_string_to_none(data.get('brand_name'))
        )

class ReviewPoint(BasePoint):
    payload: ReviewPointPayload

