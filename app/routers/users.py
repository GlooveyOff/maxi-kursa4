from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.user import UserOut
from pydantic import BaseModel


router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_teacher: bool | None = None


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.is_teacher is not None:
        # любой может стать преподавателем (упрощенно для курсовой)
        user.is_teacher = data.is_teacher
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
