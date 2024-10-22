from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.router import router as users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get("/")
def home_page():
    return {"message": "Hello world!"}


app.include_router(users_router)
