from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users, categories, courses, lessons, enrollments, progress, reviews
import app.models.progress  # noqa: F401  чтоб таблица создалась
import app.models.review  # noqa: F401


app = FastAPI(
    title="EduPlatform API",
    description="Backend образовательной платформы с курсами",
    version="1.0.0",
)

# CORS — чтобы фронт мог обращаться к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём таблицы при старте (для курсовой, в проде лучше через alembic)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(enrollments.router)
app.include_router(progress.router)
app.include_router(reviews.router)


@app.get("/")
def root():
    return {"message": "EduPlatform API работает", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
