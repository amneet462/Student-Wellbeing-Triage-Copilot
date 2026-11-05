"""
app/main.py
────────────
FastAPI application entry point for the AI Student Wellbeing Triage Engine.

This module wires together:
  • FastAPI application configuration
  • Router registration
  • CORS middleware
  • Startup/shutdown lifecycle hooks
  • Global exception handling

This is NOT a clinical tool. See the disclaimer in config.py.
"""

from __future__ import annotations

import logging
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.triage_routes import router as triage_router
from app.config import (
    API_PREFIX,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    CLINICAL_DISCLAIMER,
    CORS_ORIGINS,
    LOG_LEVEL,
    BASE_DIR,
)

from contextlib import asynccontextmanager

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ── Lifespan Context ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("Student Wellbeing Triage Engine v%s started.", APP_VERSION)
    logger.info("DISCLAIMER: %s", CLINICAL_DISCLAIMER)
    logger.info("API docs available at /docs")
    logger.info("=" * 60)
    yield
    logger.info("Student Wellbeing Triage Engine shutting down.")

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "University Wellbeing Team",
        "url": "https://your-university.ac.uk/wellbeing",
    },
    license_info={"name": "Internal Use Only"},
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(triage_router, prefix=API_PREFIX)

STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Root endpoint (Serves Web Dashboard) ──────────────────────────────────────
@app.get("/", tags=["Dashboard"], response_model=None)
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "service": APP_TITLE,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{API_PREFIX}/triage/health",
        "disclaimer": CLINICAL_DISCLAIMER,
    }


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal error occurred.",
            "detail": "Please try again or contact support.",
            "disclaimer": CLINICAL_DISCLAIMER,
        },
    )




# ── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower(),
    )

