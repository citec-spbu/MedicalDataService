from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.router import router as users_router
from app.upload.router import router as upload_router
from app.broker import broker

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

app.include_router(upload_router)

@app.on_event("startup")
async def startup_event():
    await broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await broker.close()