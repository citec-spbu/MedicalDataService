from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.users.router import router as users_router
from app.upload.router import router as upload_router
from app.download.router import router as download_router
from app.dicom_processing.processor import router as processor_router
from app.metadata_provider.router import router as metadata_router
from app.edit.router import router as edit_router
from fastapi.responses import JSONResponse
import logging

# логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


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
app.include_router(download_router)
app.include_router(processor_router)
app.include_router(metadata_router)
app.include_router(edit_router)