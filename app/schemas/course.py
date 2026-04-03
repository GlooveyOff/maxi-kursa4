from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    title: str
    description: str | None = None
    price: float = 0.0
    category_id: int | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: int | None = None
    is_published: bool | None = None


class CourseOut(CourseBase):
    id: int
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
