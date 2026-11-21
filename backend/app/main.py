from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.engine.registry import init_default_tools

from app.api.auth import router as auth_router
from app.api.profiles import router as profiles_router
from app.api.campaigns import router as campaigns_router
from app.api.drafts import router as drafts_router
from app.api.executions import router as executions_router
from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.integrations import router as integrations_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("kore")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up KORE Autonomous Outreach Platform...")
    await connect_to_mongo()
    init_default_tools()
    yield
    # Shutdown
    logger.info("Shutting down KORE...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous AI-Powered Professional Outreach Platform for ambitious students.",
    lifespan=lifespan
)

# CORS Middleware: Explicit origins only (never wildcard '*' when allow_credentials=True)
allowed_origins = [
    origin.strip() for origin in [
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ] if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(profiles_router, prefix=settings.API_V1_STR)
app.include_router(campaigns_router, prefix=settings.API_V1_STR)
app.include_router(drafts_router, prefix=settings.API_V1_STR)
app.include_router(executions_router, prefix=settings.API_V1_STR)
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(contacts_router, prefix=settings.API_V1_STR)
app.include_router(integrations_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "product": "KORE",
        "tagline": "Find the right people. Build meaningful connections.",
        "status": "operational",
        "version": settings.VERSION
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
