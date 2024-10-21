from fastapi import FastAPI
from app.users.router import router as users_router

app = FastAPI()


@app.get("/")
def home_page():
    return {"message": "Hello world!"}


app.include_router(users_router)
