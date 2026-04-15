from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Enrollment, User
from app.schemas.enrollment import EnrollmentOut, EnrollmentWithCourse


router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("/{course_id}", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    if not course.is_published:
        raise HTTPException(status_code=400, detail="Курс не опубликован")
    if course.author_id == user.id:
        raise HTTPException(status_code=400, detail="Нельзя записаться на свой курс")

    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Вы уже записаны на этот курс")
    db.refresh(enrollment)
    return enrollment


@router.get("/my", response_model=list[EnrollmentWithCourse])
def my_enrollments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id)
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user.id,
        Enrollment.course_id == course_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Вы не записаны на этот курс")
    db.delete(enrollment)
    db.commit()
