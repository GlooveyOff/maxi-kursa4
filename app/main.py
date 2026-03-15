from fastapi import FastAPI

app = FastAPI(title="EduPlatform API")


@app.get("/")
def root():
    return {"message": "EduPlatform API работает"}
