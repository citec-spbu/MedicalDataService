from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.router import router as users_router
from app.dicom_file.router import router as dicom_router
from app.broker.router import router as broker_router

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
app.include_router(dicom_router)
app.include_router(broker_router)
