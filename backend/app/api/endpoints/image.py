import logging
import urllib.parse
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.library_state import library_state

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/image", tags=["assets"], summary="Serve image")
async def serve_image(path: str):
    """
    Serve image files from the manga library with security validation.

    Args:
        path: Encoded path of the image to be served

    Returns:
        FileResponse: Requested image file

    Raises:
        HTTPException: If the library is not configured, file not found,
                      or outside security boundaries
    """

    try:
        logger.info(f"[IMAGE] Path received: {path}")

        if not library_state.current_path:
            raise HTTPException(status_code=400, detail="Library not configured")

        decoded_path = urllib.parse.unquote(path)
        logger.info(f"[IMAGE] Decoded path: {decoded_path}")

        if "/api/image?path=" in decoded_path:
            logger.info("[IMAGE] Fixing double encoding...")
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(decoded_path)
            if parsed.query:
                query_params = urlparse.parse_qs(parsed.query)
                if 'path' in query_params:
                    decoded_path = query_params['path'][0]
                    logger.info(f"[IMAGE] Actual path extracted: {decoded_path}")
                else:
                    raise HTTPException(status_code=400, detail="'path' parameter not found")

        file_path = Path(decoded_path).resolve()
        library_root = Path(library_state.current_path).resolve()

        logger.info(f"[IMAGE] File: {file_path}")
        logger.info(f"[IMAGE] Library: {library_root}")

        if not str(file_path).startswith(str(library_root)):
            logger.info(f"Path outside library: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")

        if not file_path.exists() or not file_path.is_file():
            logger.info(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")

        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        if file_path.suffix.lower() not in image_extensions:
            logger.warning(f"Attempt to access non-image file: {file_path}")
            raise HTTPException(status_code=400, detail="File type not allowed")

        logger.info(f"Serving image: {file_path.name}")
        return FileResponse(path=str(file_path))

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
