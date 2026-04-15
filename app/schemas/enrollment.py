from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.course import CourseOut


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    user_id: int
    enrolled_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithCourse(BaseModel):
    id: int
    enrolled_at: datetime
    course: CourseOut
    model_config = ConfigDict(from_attributes=True)
