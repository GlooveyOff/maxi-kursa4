from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_teacher
from app.models import Course, User
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut


router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseOut])
def list_courses(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Поиск по названию"),
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    free_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Course).filter(Course.is_published == True)

    if q:
        query = query.filter(Course.title.ilike(f"%{q}%"))
    if category_id is not None:
        query = query.filter(Course.category_id == category_id)
    if min_price is not None:
        query = query.filter(Course.price >= min_price)
    if max_price is not None:
        query = query.filter(Course.price <= max_price)
    if free_only:
        query = query.filter(Course.price == 0)

    return query.order_by(Course.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/mine", response_model=list[CourseOut])
def my_courses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # курсы, которые я создал (для преподавателя)
    return db.query(Course).filter(Course.author_id == user.id).order_by(Course.created_at.desc()).all()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_teacher),
):
    course = Course(
        title=data.title,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        author_id=user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    if course.author_id != user.id:
        raise HTTPException(status_code=403, detail="Это не ваш курс")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    if course.author_id != user.id:
        raise HTTPException(status_code=403, detail="Это не ваш курс")
    db.delete(course)
    db.commit()
