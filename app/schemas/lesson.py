from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LessonBase(BaseModel):
    title: str
    content: str | None = None
    video_url: str | None = None
    order_index: int = 0


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    video_url: str | None = None
    order_index: int | None = None


class LessonOut(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
