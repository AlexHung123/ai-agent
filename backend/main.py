from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.chat import router as chat_router
from app.api.chats import router as chats_router
from app.api.search import router as search_router
from app.api.config import router as config_router
from app.api.models import router as models_router
from app.api.suggestions import router as suggestions_router
from app.api.uploads import router as uploads_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Perplexica Backend",
    description="AI-powered search and chat backend",
    version="1.11.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://192.168.56.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(chats_router, prefix="/api", tags=["chats"])
app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(config_router, prefix="/api", tags=["config"])
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(suggestions_router, prefix="/api", tags=["suggestions"])
app.include_router(uploads_router, prefix="/api", tags=["uploads"])

@app.get("/")
async def root():
    return {"message": "Perplexica Backend API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
