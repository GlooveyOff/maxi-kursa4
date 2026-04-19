from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProgressOut(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseProgressStats(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    percent: float
