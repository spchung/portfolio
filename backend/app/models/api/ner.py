from typing import List, Iterator
from pydantic import BaseModel, Field

class EntityResults(BaseModel):
    """Pydantic model for entity extraction results."""
    skin_condition: List[str] = Field(default_factory=list, alias="SKIN_CONDITION")
    skin_description: List[str] = Field(default_factory=list, alias="SKIN_DESCRIPTION")
    body_part: List[str] = Field(default_factory=list, alias="BODY_PART")
    product_ingredient: List[str] = Field(default_factory=list, alias="PRODUCT_INGREDIENT")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
    
    def __iter__(self) -> Iterator[tuple[str, List[str]]]:
        """Make the model iterable, yielding category and values."""
        yield "SKIN_CONDITION", self.skin_condition
        yield "SKIN_DESCRIPTION", self.skin_description
        yield "BODY_PART", self.body_part
        yield "PRODUCT_INGREDIENT", self.product_ingredient
    
    def __getitem__(self, key: str) -> List[str]:
        """Allow dictionary-like access to categories."""
        if key == "SKIN_CONDITION":
            return self.skin_condition
        elif key == "SKIN_DESCRIPTION":
            return self.skin_description
        elif key == "BODY_PART":
            return self.body_part
        elif key == "PRODUCT_INGREDIENT":
            return self.product_ingredient
        else:
            raise KeyError(f"Category '{key}' not found")