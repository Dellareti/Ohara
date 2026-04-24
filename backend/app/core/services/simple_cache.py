import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.models.manga import Manga

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple and efficient cache for the manga system.
    
    Core features:
    - Timestamp-based metadata caching
    - Automatic invalidation when directory changes
    - Basic operations: load, save, clear
    """
    
    def __init__(self):
        self.cache_file_name = '.ohara_cache.json'
        
    def load_cache(self, cache_file: Path) -> Dict:
        """Load cache with basic validation"""
        if not cache_file.exists():
            return {}
        
        try:
            cache_data = json.loads(cache_file.read_text(encoding='utf-8'))
            if isinstance(cache_data, dict):
                logger.info(f"Cache loaded: {len(cache_data)} entries")
                return cache_data
        except Exception as e:
            logger.warning(f"Invalid cache, recreating: {e}")
        
        return {}
    
    def save_cache(self, cache_file: Path, mangas: List[Manga]) -> None:
        """Save cache with essential data"""
        try:
            cache_data = {}
            
            for manga in mangas:
                manga_path = Path(manga.path)
                dir_mtime = manga_path.stat().st_mtime
                
                cache_data[manga.id] = {
                    'manga_data': self._create_cache_data(manga),
                    'dir_mtime': dir_mtime
                }
            
            cache_file.write_text(
                json.dumps(cache_data, separators=(',', ':'), ensure_ascii=False),
                encoding='utf-8'
            )
            
            logger.info(f"Cache saved: {len(cache_data)} manga titles")
            
        except Exception as e:
            logger.warning(f"Error saving cache: {e}")
    
    def is_valid(self, manga_dir: Path, cache_entry: Optional[Dict]) -> bool:
        """Check if cache is valid based on directory timestamp"""
        if not cache_entry:
            return False
        
        try:
            dir_mtime = manga_dir.stat().st_mtime
            cached_mtime = cache_entry.get('dir_mtime', 0)
            return abs(dir_mtime - cached_mtime) < 1.0
        except OSError:
            return False
    
    def restore_manga(self, manga_data: Dict) -> Optional[Manga]:
        """Restore manga from cache"""
        try:
            return Manga(**manga_data)
        except Exception as e:
            logger.warning(f"Error restoring manga: {e}")
            return None
    
    def clear_cache(self, library_path: str) -> bool:
        """Clear cache"""
        try:
            cache_file = Path(library_path) / self.cache_file_name
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cache cleared: {cache_file}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
            return False
    
    def get_cache_info(self, library_path: str) -> Dict:
        """Basic cache information"""
        cache_file = Path(library_path) / self.cache_file_name
        
        if not cache_file.exists():
            return {"exists": False}
        
        try:
            stat = cache_file.stat()
            cache_data = self.load_cache(cache_file)
            
            return {
                "exists": True,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "entries": len(cache_data)
            }
        except Exception:
            return {"exists": True, "error": "Error reading cache"}
    
    def _create_cache_data(self, manga: Manga) -> Dict:
        """Create optimized cache data"""
        chapters_data = []
        
        for chapter in manga.chapters:
            chapters_data.append({
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "path": chapter.path,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
                "pages": []
            })
        
        return {
            "id": manga.id,
            "title": manga.title,
            "path": manga.path,
            "thumbnail": manga.thumbnail,
            "chapters": chapters_data,
            "chapter_count": manga.chapter_count,
            "total_pages": manga.total_pages,
            "date_added": manga.date_added.isoformat() if manga.date_added else None,
            "date_modified": manga.date_modified.isoformat() if manga.date_modified else None
        }