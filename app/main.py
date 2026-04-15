from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, users, categories, courses, lessons, enrollments


app = FastAPI(title="EduPlatform API")

# создаём таблицы при старте (для курсовой, в проде лучше через alembic)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(enrollments.router)


@app.get("/")
def root():
    return {"message": "EduPlatform API работает"}
