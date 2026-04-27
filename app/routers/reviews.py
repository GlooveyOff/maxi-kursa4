from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Enrollment, User
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut, CourseRatingStats


router = APIRouter(prefix="/courses/{course_id}/reviews", tags=["reviews"])


@router.get("/", response_model=list[ReviewOut])
def list_reviews(course_id: int, db: Session = Depends(get_db)):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Курс не найден")
    return db.query(Review).filter(Review.course_id == course_id).order_by(Review.created_at.desc()).all()


@router.get("/stats", response_model=CourseRatingStats)
def review_stats(course_id: int, db: Session = Depends(get_db)):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Курс не найден")

    avg, cnt = db.query(func.avg(Review.rating), func.count(Review.id)).filter(
        Review.course_id == course_id
    ).one()

    return CourseRatingStats(
        course_id=course_id,
        average=round(float(avg or 0), 2),
        count=cnt,
    )


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    course_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # отзыв может оставить только тот кто записан на курс
    enrolled = db.query(Enrollment).filter(
        Enrollment.user_id == user.id,
        Enrollment.course_id == course_id,
    ).first()
    if not enrolled:
        raise HTTPException(status_code=403, detail="Сначала запишитесь на курс")

    review = Review(
        user_id=user.id,
        course_id=course_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Вы уже оставляли отзыв")
    db.refresh(review)
    return review
