from pydantic import BaseModel
from typing import List

# base class for all Points
class BasePoint(BaseModel):
    id: str
    vector: List[float]
