import logging
from fastapi import APIRouter, HTTPException

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


@router.get("/api/cache/info", tags=["cache"], summary="Cache information")
async def get_cache_info():
    """
    Returns information about the current cache state.

    Returns:
        dict: Detailed cache information
    """
    if not library_state.current_path:
        return {
            "cache_enabled": True,
            "current_library": None,
            "cache_info": {"exists": False}
        }

    try:
        cache_info = scanner.get_cache_info(library_state.current_path)
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": library_state.current_path,
            "cache_info": cache_info,
            "scanner_version": "Simple Cache v2.0"
        }
    except Exception as e:
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": library_state.current_path,
            "cache_info": {"exists": False, "error": str(e)},
            "scanner_version": "Simple Cache v2.0"
        }


@router.post("/api/cache/clear", tags=["cache"], summary="Clear cache")
async def clear_cache():
    """
    Clears the cache for the current library.

    Returns:
        dict: Result of the clear operation

    Raises:
        HTTPException: If no library is configured
    """
    if not library_state.current_path:
        raise HTTPException(status_code=400, detail="No library configured")

    try:
        success = scanner.clear_cache(library_state.current_path)
        if success:
            return {"message": "Cache cleared successfully", "library_path": library_state.current_path, "status": "cleared"}
        else:
            return {"message": "No cache found to clear", "library_path": library_state.current_path, "status": "no_cache"}
    except Exception as e:
        logger.warning(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.post("/api/cache/disable", tags=["cache"], summary="Disable cache")
async def disable_cache():
    """
    Disables the cache system.

    Returns:
        dict: Confirmation of disabling

    Raises:
        HTTPException: If an error occurs during the operation
    """
    try:
        scanner.disable_cache()
        return {"message": "Cache disabled", "cache_enabled": False, "status": "disabled"}
    except Exception as e:
        logger.warning(f"Error disabling cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error disabling cache: {str(e)}")


@router.post("/api/cache/enable", tags=["cache"], summary="Enable cache")
async def enable_cache():
    """
    Enables the cache system.

    Returns:
        dict: Confirmation of enabling

    Raises:
        HTTPException: If an error occurs during the operation
    """
    try:
        scanner.enable_cache()
        return {"message": "Cache enabled", "cache_enabled": True, "status": "enabled"}
    except Exception as e:
        logger.warning(f"Error enabling cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enabling cache: {str(e)}")