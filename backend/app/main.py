import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.reader import router as reader_router
from app.api.endpoints.library import router as library_router
from app.api.endpoints.manga import router as manga_router
from app.api.endpoints.cache import router as cache_router
from app.api.endpoints.debug import router as debug_router
from app.api.endpoints.image import router as image_router
from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from log_config import log_config

logger = logging.getLogger(__name__)

# Initialize MangaScanner and load settings
scanner = MangaScanner()
library_state.load_from_file()

# FastAPI application configuration
app = FastAPI(
    title="Ohara Manga Reader API",
    description="""
    API for manga library management and reading.
    
    ## Features
    
    * **Library**: Scanning and management of manga libraries
    * **Manga**: Viewing manga details and chapters
    * **Reader**: Reading progress system and navigation
    * **Cache**: Hybrid cache system for better performance
    * **Images**: Image server with security validation
    * **Debug**: Debug and monitoring tools
    
    ## Data Structure
    
    Manga is organized as:
    - **Library** → contains multiple manga titles
    - **Manga** → contains multiple chapters  
    - **Chapter** → contains multiple pages
    - **Page** → individual image file
    
    ## Setup
    
    To use the API:
    1. Configure a library with `POST /api/scan-library`
    2. Browse available manga with `GET /api/library`
    3. Read specific manga with `GET /api/manga/{manga_id}`
    """,
    version="2.0.0",
    contact={
        "name": "Ohara Development Team",
        "url": "https://github.com/Dellareti/ohara",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register module routers
app.include_router(reader_router, prefix="", tags=["reader"])
app.include_router(library_router, prefix="", tags=["library"])
app.include_router(manga_router, prefix="", tags=["manga"])
app.include_router(cache_router, prefix="", tags=["cache"])
app.include_router(debug_router, prefix="", tags=["debug"])
app.include_router(image_router, prefix="", tags=["assets"])


@app.get("/", tags=["root"], summary="API Information")
async def root():
    """
    Root endpoint with basic API information.
    
    Returns:
        dict: Information about the API and its status
    """
    
    return {
        "name": "Ohara Manga Reader API",
        "version": "2.0.0",
        "description": "API for manga library management and reading",
        "status": "online",
        "library_configured": library_state.current_path is not None,
        "current_library": library_state.current_path,
        "endpoints": {
            "library": "/api/library",
            "scan": "/api/scan-library", 
            "manga": "/api/manga/{manga_id}",
            "reader": "/api/manga/{manga_id}/chapters",
            "cache": "/api/cache/info",
            "debug": "/api/debug"
        }
    }


@app.get("/health", tags=["health"], summary="Health check")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Application and dependencies status
    """
    
    return {
        "status": "healthy",
        "library_state": "configured" if library_state.current_path else "not_configured",
        "scanner_enabled": True,
        "cache_enabled": scanner.cache_enabled
    }


@app.get("/api/test", tags=["test"], summary="API Test")
async def test_api():
    """
    Test endpoint to verify basic API functionality.
    
    Returns:
        dict: Confirmation of operation
    """
    
    return {
        "message": "API is working correctly!",
        "timestamp": "2024-01-01T00:00:00Z",
        "test": "success"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=log_config,
        log_level="info"
    )