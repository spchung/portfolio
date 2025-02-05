from dataclasses import dataclass
from pydantic import BaseModel

class MilvusSearchResultItem(BaseModel):
    id: int
    distance: float