"""
QA Guardian - Aplicacion Principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.diagnosis import router as diagnosis_router
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"Environment: {settings.ENVIRONMENT}")
    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Diagnostic Engine API",
    lifespan=lifespan,
)

_origins = settings.CORS_ORIGINS or ["*"]
_wildcard = _origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=not _wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)

app.include_router(diagnosis_router)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
