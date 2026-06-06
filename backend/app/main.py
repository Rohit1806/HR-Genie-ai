from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import structlog

from app.config import settings
from app.database import init_db
from app.redis_client import init_redis, close_redis
from app.api.v1.router import api_router
from app.core.middleware import AuditLogMiddleware, RequestIDMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting HRGenie AI", version=settings.APP_VERSION)
    await init_redis()
    
    # Run migrations and seed data on startup
    try:
        import subprocess
        import sys
        import os
        
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        logger.info("Running database migrations (Alembic upgrade head)...")
        subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], 
                      cwd=backend_dir,
                      check=True)
        logger.info("Migrations completed successfully.")
        
        logger.info("Seeding database demo data...")
        subprocess.run([sys.executable, 'scripts/seed_demo_data.py'],
                      cwd=backend_dir,
                      check=True)
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Startup database initialization error: {e}")
        
    yield
    # Shutdown
    await close_redis()
    logger.info("HRGenie AI stopped")


# Create FastAPI app
app = FastAPI(
    title="HRGenie AI",
    description="Next-Generation AI-Powered HR Management Platform",
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ─── MIDDLEWARE (order matters) ────────────────────────────────────────────────

# 1. Request ID (first — needed by all other middleware)
app.add_middleware(RequestIDMiddleware)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# 4. Audit Log
app.add_middleware(AuditLogMiddleware)

# ─── ROUTES ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["root"])
async def root():
    return {"message": "HRGenie AI API", "docs": "/docs"}
