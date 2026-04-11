from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Lesson, User
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonOut


router = APIRouter(prefix="/courses/{course_id}/lessons", tags=["lessons"])


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


@router.get("/", response_model=list[LessonOut])
def list_lessons(course_id: int, db: Session = Depends(get_db)):
    _get_course_or_404(db, course_id)
    return (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.order_index)
        .all()
    )


@router.post("/", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def create_lesson(
    course_id: int,
    data: LessonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = _get_course_or_404(db, course_id)
    if course.author_id != user.id:
        raise HTTPException(status_code=403, detail="Это не ваш курс")

    lesson = Lesson(course_id=course_id, **data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.patch("/{lesson_id}", response_model=LessonOut)
def update_lesson(
    course_id: int,
    lesson_id: int,
    data: LessonUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = _get_course_or_404(db, course_id)
    if course.author_id != user.id:
        raise HTTPException(status_code=403, detail="Это не ваш курс")

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, Lesson.course_id == course_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = _get_course_or_404(db, course_id)
    if course.author_id != user.id:
        raise HTTPException(status_code=403, detail="Это не ваш курс")
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, Lesson.course_id == course_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    db.delete(lesson)
    db.commit()
