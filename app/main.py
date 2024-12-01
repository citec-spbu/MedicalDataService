from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.router import router as users_router
from app.upload.router import router as upload_router
from app.dicom_processing.processor import router as processor_router
from app.metadata_provider.router import router as metadata_router
import logging

# логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("Starting up application...")

@app.on_event("shutdown")
async def shutdown_event():
    """Корректное завершение работы приложения"""
    logger.info("Shutting down application...")

@app.get("/")
def home_page():
    return {"message": "Hello world!"}

app.include_router(users_router)
app.include_router(upload_router)
app.include_router(processor_router)
app.include_router(metadata_router)