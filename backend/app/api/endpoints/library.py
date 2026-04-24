import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from app.models.manga import LibraryResponse

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


def manga_to_dict(manga):
    """
    Converts a Manga object to a dictionary, handling special fields like datetime
    """
    manga_dict = {
        "id": manga.id,
        "title": manga.title,
        "path": manga.path,
        "thumbnail": manga.thumbnail,
        "chapter_count": manga.chapter_count,
        "total_pages": manga.total_pages,
        "author": manga.author,
        "artist": manga.artist,
        "status": manga.status,
        "description": manga.description,
        "genres": manga.genres,
        "date_added": manga.date_added.isoformat() if manga.date_added else None,
        "date_modified": manga.date_modified.isoformat() if manga.date_modified else None,
        "chapters": []
    }
    for chapter in manga.chapters:
        chapter_dict = {
            "id": chapter.id,
            "name": chapter.name,
            "number": chapter.number,
            "volume": chapter.volume,
            "path": chapter.path,
            "page_count": chapter.page_count,
            "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
            "pages": []
        }
        manga_dict["chapters"].append(chapter_dict)
    return manga_dict


def _scan_library_common(library_path: str, method: str = "POST"):
    """
    Common logic for scanning a library (used by both POST and GET)
    """
    library_path = library_path.strip()
    logger.info(f"[{method}] Path received: '{library_path}'")
    if method == "POST":
        logger.info(f"Length: {len(library_path)} characters")
        logger.info(f"Encoding: {library_path.encode('utf-8')}")

    if library_state.current_path != library_path:
        logger.info(f"[{method}] Changing library from '{library_state.current_path}' to '{library_path}'")
        library_state.clear()

    if method == "POST":
        try:
            path_obj = Path(library_path)
            logger.info(f"Path object created: {path_obj}")
            logger.info(f"Absolute path: {path_obj.absolute()}")
        except Exception as path_error:
            logger.warning(f"Error creating Path object: {path_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid path (encoding error): {library_path}"
            )
    else:
        path_obj = Path(library_path)
        logger.info(f"[{method}] Path object created: {path_obj}")

    if not path_obj.exists():
        if method == "POST":
            alternative_paths = [
                Path(library_path.encode('utf-8').decode('utf-8')),
                Path(library_path.encode('latin-1').decode('utf-8', errors='ignore')),
            ]
            path_found = False
            for alt_path in alternative_paths:
                try:
                    if alt_path.exists():
                        path_obj = alt_path
                        library_path = str(alt_path)
                        path_found = True
                        logger.info(f"Path found with alternative encoding: {library_path}")
                        break
                except:
                    continue
            if not path_found:
                raise HTTPException(status_code=400, detail=f"Path not found: {library_path}")
        else:
            raise HTTPException(status_code=400, detail=f"Path not found: {library_path}")

    if not path_obj.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {library_path}")

    if not os.access(str(path_obj), os.R_OK):
        raise HTTPException(status_code=403, detail=f"No read permission: {library_path}")

    subdirs = [d for d in path_obj.iterdir() if d.is_dir()]
    if len(subdirs) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Folder contains no subdirectories (manga): {library_path}"
        )

    logger.info(f"Scanning library: {library_path}")
    library = scanner.scan_library(str(path_obj))
    library_state.current_path = str(path_obj)
    logger.info(f"Library scanned: {library.total_mangas} manga titles found")

    response_data = {
        "library": {
            "mangas": [manga_to_dict(manga) for manga in library.mangas],
            "total_mangas": library.total_mangas,
            "total_chapters": library.total_chapters,
            "total_pages": library.total_pages,
            "last_updated": library.last_updated.isoformat()
        },
        "message": f"Library scanned successfully! {library.total_mangas} manga titles found.",
        "scanned_path": str(path_obj),
        "timestamp": library.last_updated.isoformat()
    }
    if method == "GET":
        response_data["method"] = "GET"
    return response_data


@router.post("/api/clear-library")
async def clear_library():
    try:
        logger.info("Clearing library in backend...")
        library_state.clear()
        logger.info("Library cleared in backend")
        return {"message": "Library cleared successfully", "current_path": None, "status": "cleared"}
    except Exception as e:
        logger.warning(f"Error clearing library: {str(e)}")
        return {"message": f"Error clearing library: {str(e)}", "status": "error"}


@router.post("/api/scan-library", tags=["library"], summary="Scan library")
async def scan_library_path(library_path: str = Form(...)):
    """
    Scans a system folder to find organized manga titles.

    Args:
        library_path: Absolute path to the library folder

    Returns:
        LibraryResponse: Scanned library with found manga titles

    Raises:
        HTTPException: If the path does not exist or permissions are missing
    """
    try:
        response_data = _scan_library_common(library_path, "POST")
        return JSONResponse(content=jsonable_encoder(response_data))
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error scanning library: {str(e)}")
        logger.warning(f"Error type: {type(e).__name__}")
        import traceback
        logger.warning(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error scanning library: {str(e)}")


@router.get("/api/scan-library", tags=["library"], summary="Scan saved library")
async def scan_saved_library():
    """
    Scans the previously saved library.

    Returns:
        LibraryResponse: Scanned library with found manga titles

    Raises:
        HTTPException: If no library is configured
    """
    current_path = library_state.current_path
    if not current_path:
        raise HTTPException(
            status_code=400,
            detail="No library configured. Use POST /api/scan-library to configure."
        )
    try:
        response_data = _scan_library_common(current_path, "GET")
        return JSONResponse(content=jsonable_encoder(response_data))
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error scanning saved library: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error scanning library: {str(e)}")


@router.get("/api/library", tags=["library"], summary="Get current library")
async def get_library():
    """
    Returns the currently configured library.

    Returns:
        dict: Information about the current library

    Raises:
        HTTPException: If no library is configured
    """
    current_path = library_state.current_path
    if not current_path:
        raise HTTPException(status_code=400, detail="No library configured")
    if not library_state.validate_current_path():
        raise HTTPException(status_code=400, detail=f"Invalid library path: {current_path}")
    try:
        library = scanner.scan_library(current_path)
        response_data = {
            "library": {
                "mangas": [manga_to_dict(manga) for manga in library.mangas],
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "last_updated": library.last_updated.isoformat()
            },
            "current_path": current_path,
            "message": f"Library loaded: {library.total_mangas} manga titles found"
        }
        return JSONResponse(content=jsonable_encoder(response_data))
    except Exception as e:
        logger.warning(f"Error loading library: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading library: {str(e)}")


@router.get("/api/validate-path", tags=["library"], summary="Validate library path")
async def validate_library_path(path: str):
    """
    Validates whether a path can be used as a manga library.

    Args:
        path: Path to be validated

    Returns:
        dict: Validation result
    """
    try:
        is_valid, message = scanner.validate_library_path(path)
        return {"path": path, "is_valid": is_valid, "message": message, "current_library": library_state.current_path}
    except Exception as e:
        logger.warning(f"Error validating path: {str(e)}")
        return {"path": path, "is_valid": False, "message": f"Error validating: {str(e)}", "current_library": library_state.current_path}


@router.get("/api/preview-library", tags=["library"], summary="Library preview")
async def preview_library(path: str):
    """
    Provides a quick preview of a library without configuring it.

    Args:
        path: Library path for preview

    Returns:
        dict: Preview with basic library information
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        if not path_obj.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        subdirs = [d for d in path_obj.iterdir() if d.is_dir()]
        total_folders = len(subdirs)
        estimated_chapters = 0
        sampled_mangas = 0

        for manga_dir in subdirs[:10]:
            try:
                chapter_dirs = [d for d in manga_dir.iterdir() if d.is_dir()]
                estimated_chapters += len(chapter_dirs)
                sampled_mangas += 1
            except:
                continue

        if sampled_mangas > 0:
            avg_chapters_per_manga = estimated_chapters / sampled_mangas
            estimated_total_chapters = int(avg_chapters_per_manga * total_folders)
        else:
            estimated_total_chapters = 0

        return {
            "path": str(path_obj),
            "total_manga_folders": total_folders,
            "estimated_chapters": estimated_total_chapters,
            "sampled_mangas": sampled_mangas,
            "is_valid": total_folders > 0,
            "message": f"Preview: {total_folders} manga folders found"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error in library preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in preview: {str(e)}")


@router.post("/api/set-library-path", tags=["library"], summary="Set library path")
async def set_library_path(library_path: str = Form(...)):
    """
    Sets the library path without scanning it.

    Args:
        library_path: Library path

    Returns:
        dict: Configuration confirmation
    """
    try:
        library_path = library_path.strip()
        path_obj = Path(library_path)
        if not path_obj.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        if not path_obj.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        library_state.current_path = str(path_obj)
        return {"message": "Library path configured successfully", "library_path": str(path_obj), "status": "configured"}
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error configuring library: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error configuring library: {str(e)}")