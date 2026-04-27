from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    rating: int
    comment: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseRatingStats(BaseModel):
    course_id: int
    average: float
    count: int
