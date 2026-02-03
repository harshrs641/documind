
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, search
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Document ingestion and search API for technical documentation",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(search.router)

@app.get("/")
async def root():
    return {
        "message": "DocuMind API - Document Ingestion Service",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# To run the application:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000