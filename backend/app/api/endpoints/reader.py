import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner

logger = logging.getLogger(__name__)

def chapter_to_dict(chapter) -> dict:
    return {
        "id": chapter.id,
        "name": chapter.name,
        "number": chapter.number,
        "volume": chapter.volume,
        "path": chapter.path,
        "page_count": chapter.page_count,
        "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
        "pages": [
            {
                "filename": page.filename,
                "path": page.path,
                "size": page.size,
                "width": page.width,
                "height": page.height
            }
            for page in chapter.pages
        ]
    }

router = APIRouter()
scanner = MangaScanner()

# Global cache for chapter data
_chapter_cache = {}

def _find_chapter_flexible(manga, chapter_id: str):
    """
    Accepts:
    - Exact ID: "kagurabachi-ch-78.0"
    - Custom slug: "sirius-scanlator-chapter-78-replacement"
    - By number: "78", "78.0"
    - By partial name: "Chapter 78"
    """
    logger.info(f"Searching for chapter: '{chapter_id}'")

    # 1. Search by exact ID (fastest)
    for chapter in manga.chapters:
        if chapter.id == chapter_id:
            logger.info(f"Found by exact ID: {chapter.id}")
            return chapter

    # 2. Search by chapter number
    try:
        numbers = re.findall(r'(\d+(?:\.\d+)?)', chapter_id)
        if numbers:
            search_number = float(numbers[0])
            for chapter in manga.chapters:
                if chapter.number == search_number:
                    logger.info(f"Found by number: {chapter.number} -> {chapter.id}")
                    return chapter
    except Exception as e:
        logger.warning(f"Error searching by number: {e}")

    # 3. Search by partial name (fallback)
    chapter_id_lower = chapter_id.lower()
    for chapter in manga.chapters:
        chapter_name_lower = chapter.name.lower()
        clean_id = re.sub(r'[^\w\s]', '', chapter_id_lower)
        clean_name = re.sub(r'[^\w\s]', '', chapter_name_lower)
        if clean_id in clean_name or clean_name in clean_id:
            logger.info(f"Found by partial name: '{chapter_id}' -> {chapter.id}")
            return chapter

    # 4. Search by keywords
    words_in_id = chapter_id_lower.split('-')
    for chapter in manga.chapters:
        chapter_words = re.split(r'[\s\-_]+', chapter.name.lower())
        matches = sum(1 for word in words_in_id if word in chapter_words)
        if matches >= 2:
            logger.info(f"Found by keywords ({matches} matches): {chapter.id}")
            return chapter

    # 5. Not found
    logger.warning(f"Chapter not found: '{chapter_id}'")
    logger.info(f"Available chapters:")
    for i, ch in enumerate(manga.chapters[:5]):
        logger.info(f"  {i+1}. ID: '{ch.id}' | Name: '{ch.name}' | Number: {ch.number}")

    return None

@router.get("/api/manga/{manga_id}/chapter/{chapter_id}")
async def get_chapter(manga_id: str, chapter_id: str):
    """
    Returns complete data for a specific chapter.
    Accepts multiple chapter_id formats.
    """
    if not library_state.current_path:
        raise HTTPException(status_code=400, detail="No library configured")

    try:
        logger.info(f"Chapter request: {manga_id}/{chapter_id}")

        cache_key = f"{manga_id}_{chapter_id}"
        if cache_key in _chapter_cache:
            logger.info(f"Cache hit for chapter: {chapter_id}")
            return _chapter_cache[cache_key]

        library = scanner.scan_library(library_state.current_path)
        manga = library.get_manga(manga_id)

        if not manga:
            raise HTTPException(status_code=404, detail=f"Manga '{manga_id}' not found")

        chapter = _find_chapter_flexible(manga, chapter_id)

        if not chapter:
            available_chapters = [{"id": ch.id, "name": ch.name, "number": ch.number} for ch in manga.chapters[:10]]
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Chapter '{chapter_id}' not found",
                    "manga_id": manga_id,
                    "requested_chapter_id": chapter_id,
                    "available_chapters": available_chapters,
                    "total_chapters": len(manga.chapters)
                }
            )

        chapter_data = chapter_to_dict(chapter)
        for page in chapter_data['pages']:
            if not page['path'].startswith('/api/image'):
                page['url'] = f"/api/image?path={page['path']}"
            else:
                page['url'] = page['path']

        response_data = {
            "chapter": chapter_data,
            "manga": {
                "id": manga.id,
                "title": manga.title,
                "total_chapters": manga.chapter_count
            },
            "navigation": {
                "previous_chapter": _find_previous_chapter(manga, chapter),
                "next_chapter": _find_next_chapter(manga, chapter),
                "chapter_index": _get_chapter_index(manga, chapter)
            },
            "message": f"Chapter '{chapter.name}' loaded successfully"
        }

        _chapter_cache[cache_key] = response_data
        logger.info(f"Chapter loaded: {chapter.name} ({len(chapter.pages)} pages)")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading chapter: {str(e)}")
        import traceback
        logger.info(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error loading chapter: {str(e)}")

@router.get("/api/manga/{manga_id}/chapters")
async def get_manga_chapters(manga_id: str, limit: int = Query(500, ge=1, le=1000)):
    """
    Returns list of chapters for a manga (for navigation)
    """
    if not library_state.current_path:
        raise HTTPException(status_code=400, detail="No library configured")

    try:
        library = scanner.scan_library(library_state.current_path)
        manga = library.get_manga(manga_id)

        if not manga:
            raise HTTPException(status_code=404, detail=f"Manga '{manga_id}' not found")

        chapters_summary = []
        for chapter in manga.chapters[:limit]:
            chapter_summary = {
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
                "thumbnail": chapter.pages[0].path if chapter.pages else None
            }
            if chapter_summary["thumbnail"]:
                chapter_summary["thumbnail_url"] = f"/api/image?path={chapter_summary['thumbnail']}"
            chapters_summary.append(chapter_summary)

        return {
            "manga_id": manga_id,
            "manga_title": manga.title,
            "chapters": chapters_summary,
            "total_chapters": len(manga.chapters),
            "returned_count": len(chapters_summary)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing chapters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing chapters: {str(e)}")

@router.post("/api/progress/{manga_id}/{chapter_id}")
async def save_reading_progress(
    manga_id: str,
    chapter_id: str,
    current_page: int,
    total_pages: int,
    reading_time_seconds: Optional[int] = 0
):
    """
    Saves reading progress for a chapter
    """
    try:
        progress_file = Path("reading_progress.json")
        progress_data = {}

        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)

        if manga_id not in progress_data:
            progress_data[manga_id] = {}

        progress_data[manga_id][chapter_id] = {
            "current_page": current_page,
            "total_pages": total_pages,
            "progress_percentage": round((current_page / max(total_pages - 1, 1)) * 100, 2),
            "is_completed": current_page >= total_pages - 1,
            "last_read": datetime.now().isoformat(),
            "reading_time_seconds": reading_time_seconds
        }

        progress_data[manga_id]["_manga_info"] = {
            "last_chapter_read": chapter_id,
            "last_read": datetime.now().isoformat(),
            "total_reading_time": sum(
                ch.get("reading_time_seconds", 0)
                for ch in progress_data[manga_id].values()
                if isinstance(ch, dict) and "reading_time_seconds" in ch
            )
        }

        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Progress saved: {manga_id}/{chapter_id} - Page {current_page}/{total_pages}")

        return {"message": "Progress saved successfully", "progress": progress_data[manga_id][chapter_id]}

    except Exception as e:
        logger.error(f"Error saving progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving progress: {str(e)}")

@router.get("/api/progress/{manga_id}")
async def get_manga_progress(manga_id: str):
    """
    Returns reading progress for a manga
    """
    try:
        progress_file = Path("reading_progress.json")

        if not progress_file.exists():
            return {"manga_id": manga_id, "chapters": {}, "manga_info": {}, "message": "No progress found"}

        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)

        manga_progress = progress_data.get(manga_id, {})
        manga_info = manga_progress.pop("_manga_info", {})

        return {"manga_id": manga_id, "chapters": manga_progress, "manga_info": manga_info, "message": "Progress loaded successfully"}

    except Exception as e:
        logger.error(f"Error loading progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading progress: {str(e)}")

@router.get("/api/progress/{manga_id}/{chapter_id}")
async def get_chapter_progress(manga_id: str, chapter_id: str):
    """
    Returns specific progress for a chapter
    """
    try:
        progress_file = Path("reading_progress.json")

        if not progress_file.exists():
            return {"manga_id": manga_id, "chapter_id": chapter_id, "progress": None, "message": "No progress found"}

        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)

        chapter_progress = progress_data.get(manga_id, {}).get(chapter_id)

        return {
            "manga_id": manga_id,
            "chapter_id": chapter_id,
            "progress": chapter_progress,
            "message": "Chapter progress loaded" if chapter_progress else "No progress found"
        }

    except Exception as e:
        logger.error(f"Error loading chapter progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading progress: {str(e)}")

# Helper functions
def _find_previous_chapter(manga, current_chapter):
    chapters = manga.chapters
    for i, chapter in enumerate(chapters):
        if chapter.id == current_chapter.id:
            # Check if there is a previous chapter (higher index, since list is in descending order)
            if i < len(chapters) - 1:
                prev_ch = chapters[i + 1]
                return {"id": prev_ch.id, "name": prev_ch.name, "number": prev_ch.number}
            # Reached the end of list (first chronologically)
            return None
    return None

def _find_next_chapter(manga, current_chapter):
    chapters = manga.chapters
    for i, chapter in enumerate(chapters):
        if chapter.id == current_chapter.id:
            # Check if there is a next chapter (lower index, since list is in descending order)
            if i > 0:
                next_ch = chapters[i - 1]
                return {"id": next_ch.id, "name": next_ch.name, "number": next_ch.number}
            # Reached the beginning of list (last chronologically)
            return None
    return None

def _get_chapter_index(manga, current_chapter):
    for i, chapter in enumerate(manga.chapters):
        if chapter.id == current_chapter.id:
            return {"current": i + 1, "total": len(manga.chapters)}
    return {"current": 0, "total": len(manga.chapters)}