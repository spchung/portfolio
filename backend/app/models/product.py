# sql model
from sqlmodel import Field, SQLModel
from sqlalchemy import Text, JSON, Column

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
    images: dict = Field(sa_column=Column(JSON), default_factory=dict)
    categories: str = Field(sa_column=Text())
    details: dict = Field(sa_column=Column(JSON), default_factory=dict)
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def to_dict(self):
        return self.model_dump()
