from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Enrollment, Lesson, User
from app.models.progress import LessonProgress
from app.schemas.progress import ProgressOut, CourseProgressStats


router = APIRouter(prefix="/progress", tags=["progress"])


def _check_enrolled(db: Session, user_id: int, course_id: int):
    enrolled = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
    ).first()
    if not enrolled:
        raise HTTPException(status_code=403, detail="Вы не записаны на этот курс")


@router.post("/lesson/{lesson_id}", response_model=ProgressOut, status_code=status.HTTP_201_CREATED)
def mark_lesson_done(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    _check_enrolled(db, user.id, lesson.course_id)

    progress = LessonProgress(user_id=user.id, lesson_id=lesson_id)
    db.add(progress)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Урок уже отмечен")
    db.refresh(progress)
    return progress


@router.get("/course/{course_id}", response_model=CourseProgressStats)
def course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    total = db.query(Lesson).filter(Lesson.course_id == course_id).count()
    if total == 0:
        return CourseProgressStats(
            course_id=course_id,
            total_lessons=0,
            completed_lessons=0,
            percent=0.0,
        )

    done = (
        db.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .filter(
            Lesson.course_id == course_id,
            LessonProgress.user_id == user.id,
        )
        .count()
    )

    return CourseProgressStats(
        course_id=course_id,
        total_lessons=total,
        completed_lessons=done,
        percent=round(done / total * 100, 1),
    )
