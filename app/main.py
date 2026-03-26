from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth


app = FastAPI(title="EduPlatform API")

# создаём таблицы при старте (для курсовой, в проде лучше через alembic)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "EduPlatform API работает"}
