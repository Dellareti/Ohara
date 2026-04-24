import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.core.config import get_settings, SUPPORTED_IMAGE_EXTENSIONS, THUMBNAIL_FILENAMES
from app.core.services.simple_cache import SimpleCache
from app.core.services.chapter_parser import ChapterParser
from app.models.manga import Manga, Chapter, Page, Library

logger = logging.getLogger(__name__)


class MangaScanner:
    """
    Simplified and efficient manga scanner.
    
    Core features:
    - Manga library scanning
    - Simple timestamp-based cache
    - Manga structure discovery
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.supported_extensions = SUPPORTED_IMAGE_EXTENSIONS
        self.cache_enabled = True
        
        # Core components
        self.cache = SimpleCache()
        self.chapter_parser = ChapterParser()
        
        logger.info("MangaScanner initialized (simplified mode)")

    def scan_library(self, library_path: str) -> Library:
        """Scans a manga library with simple cache"""
        library_path_obj = Path(library_path)
        
        if not library_path_obj.exists():
            raise ValueError(f"Library not found: {library_path}")
        
        # Load cache if enabled
        cache_data = {}
        if self.cache_enabled:
            cache_file = library_path_obj / self.cache.cache_file_name
            cache_data = self.cache.load_cache(cache_file)
        
        # Discover manga directories
        manga_dirs = self._discover_manga_directories(library_path_obj)
        logger.info(f"Found {len(manga_dirs)} manga directories")
        
        # Process manga titles
        mangas = []
        cache_hits = 0
        
        for manga_dir in manga_dirs:
            manga_id = self._generate_manga_id(manga_dir.name)
            cache_entry = cache_data.get(manga_id)
            
            # Try to use cache
            if self.cache_enabled and self.cache.is_valid(manga_dir, cache_entry):
                manga = self.cache.restore_manga(cache_entry['manga_data'])
                if manga:
                    # Reload pages if necessary
                    self._ensure_pages_loaded(manga)
                    mangas.append(manga)
                    cache_hits += 1
                    continue
            
            # Scan manga
            manga = self.scan_manga(str(manga_dir))
            if manga:
                mangas.append(manga)
        
        # Save updated cache
        if self.cache_enabled and mangas:
            self.cache.save_cache(library_path_obj / self.cache.cache_file_name, mangas)
        
        logger.info(f"Library scanned: {len(mangas)} manga titles ({cache_hits} from cache)")
        
        library = Library(mangas=mangas)
        library._update_stats()
        return library
    
    def scan_manga(self, manga_path: str) -> Optional[Manga]:
        """Scans a specific manga"""
        manga_path_obj = Path(manga_path)
        
        if not manga_path_obj.exists():
            return None
        
        try:
            # Discover chapters
            chapter_dirs = self._discover_chapter_directories(manga_path_obj)
            
            if not chapter_dirs:
                logger.warning(f"No chapters found in: {manga_path_obj.name}")
                return None
            
            # Process chapters
            chapters = []
            total_pages = 0
            
            for chapter_dir in chapter_dirs:
                chapter = self._scan_chapter(chapter_dir)
                if chapter:
                    chapters.append(chapter)
                    total_pages += chapter.page_count
            
            if not chapters:
                return None
            
            # Sort chapters
            chapters = self.chapter_parser.sort_chapters(chapters)
            
            # Find thumbnail
            thumbnail = self._find_thumbnail(manga_path_obj)
            
            # Create manga
            manga = Manga(
                id=self._generate_manga_id(manga_path_obj.name),
                title=manga_path_obj.name,
                path=str(manga_path_obj),
                thumbnail=thumbnail,
                chapters=chapters,
                chapter_count=len(chapters),
                total_pages=total_pages,
                date_added=datetime.now(),
                date_modified=datetime.fromtimestamp(manga_path_obj.stat().st_mtime)
            )
            
            return manga
            
        except Exception as e:
            logger.error(f"Error scanning manga {manga_path_obj.name}: {e}")
            return None
    
    def enable_cache(self):
        """Enable cache"""
        self.cache_enabled = True
        logger.info("Cache enabled")
    
    def disable_cache(self):
        """Disable cache"""
        self.cache_enabled = False
        logger.info("Cache disabled")
    
    def clear_cache(self, library_path: str) -> bool:
        """Clear library cache"""
        return self.cache.clear_cache(library_path)
    
    def get_cache_info(self, library_path: str) -> dict:
        """Get cache information"""
        return self.cache.get_cache_info(library_path)
    
    def _discover_manga_directories(self, library_path: Path) -> List[Path]:
        """Discover manga directories"""
        manga_dirs = []
        
        try:
            for item in library_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    manga_dirs.append(item)
        except OSError as e:
            logger.error(f"Error reading library: {e}")
        
        return sorted(manga_dirs)
    
    def _discover_chapter_directories(self, manga_path: Path) -> List[Path]:
        """Discover chapter directories"""
        chapter_dirs = []
        
        try:
            for item in manga_path.iterdir():
                if item.is_dir():
                    # Check if it has images
                    if self._has_images(item):
                        chapter_dirs.append(item)
        except OSError as e:
            logger.error(f"Error reading manga: {e}")
        
        return chapter_dirs
    
    def _scan_chapter(self, chapter_path: Path) -> Optional[Chapter]:
        """Scan a chapter"""
        try:
            # Find images
            image_files = self._find_image_files(chapter_path)
            
            if not image_files:
                return None
            
            # Create pages
            pages = []
            for i, image_file in enumerate(image_files, 1):
                page = Page(
                    id=f"{chapter_path.name}_page_{i}",
                    number=i,
                    filename=image_file.name,
                    path=str(image_file)
                )
                pages.append(page)
            
            # Parse chapter
            chapter_info = self.chapter_parser.parse_chapter_name(chapter_path.name)
            
            # Generate clean chapter ID
            manga_id = self._generate_manga_id(chapter_path.parent.name)
            chapter_number = chapter_info.get('number', 0)
            chapter_id = f"{manga_id}-ch-{int(chapter_number) if chapter_number else 1}"
            
            chapter = Chapter(
                id=chapter_id,
                name=chapter_path.name,
                number=chapter_info.get('number', 0),
                volume=chapter_info.get('volume'),
                path=str(chapter_path),
                pages=pages,
                page_count=len(pages),
                date_added=datetime.now()
            )
            
            return chapter
            
        except Exception as e:
            logger.error(f"Error scanning chapter {chapter_path.name}: {e}")
            return None
    
    def _find_thumbnail(self, manga_path: Path) -> Optional[str]:
        """Find manga thumbnail"""
        # Search in root folder for conventional cover filenames in multiple languages
        for ext in self.supported_extensions:
            for pattern in THUMBNAIL_FILENAMES:
                thumb_file = manga_path / f"{pattern}.{ext}"
                if thumb_file.exists():
                    return str(thumb_file)
        
        # Use first image in root folder
        for file in manga_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.supported_extensions:
                return str(file)
        
        # Use first page of first chapter
        chapter_dirs = self._discover_chapter_directories(manga_path)
        if chapter_dirs:
            first_chapter = sorted(chapter_dirs)[0]
            image_files = self._find_image_files(first_chapter)
            if image_files:
                return str(image_files[0])
        
        return None
    
    def _find_image_files(self, directory: Path) -> List[Path]:
        """Find image files in a directory"""
        image_files = []
        
        try:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in self.supported_extensions:
                    image_files.append(file)
        except OSError:
            pass
        
        return sorted(image_files)
    
    def _has_images(self, directory: Path) -> bool:
        """Check if directory has images"""
        try:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in self.supported_extensions:
                    return True
        except OSError:
            pass
        
        return False
    
    def _ensure_pages_loaded(self, manga: Manga) -> None:
        """Ensure pages are loaded for manga from cache"""
        for chapter in manga.chapters:
            if not chapter.pages:
                chapter_path = Path(chapter.path)
                if chapter_path.exists():
                    image_files = self._find_image_files(chapter_path)
                    pages = []
                    
                    for i, image_file in enumerate(image_files, 1):
                        page = Page(
                            id=f"{chapter.id}_page_{i}",
                            number=i,
                            filename=image_file.name,
                            path=str(image_file)
                        )
                        pages.append(page)
                    
                    chapter.pages = pages
                    chapter.page_count = len(pages)
    
    def _generate_manga_id(self, manga_name: str) -> str:
        """Generate readable ID for manga (compatible with previous system)"""
        import re
        clean_title = manga_name.lower()
        clean_title = re.sub(r'\W+', '-', clean_title)
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')
        return clean_title
    
    @staticmethod
    def validate_library_path(path: str) -> tuple[bool, str]:
        """Validate library path"""
        from pathlib import Path
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            return False, "Path does not exist"
        
        if not path_obj.is_dir():
            return False, "Path is not a directory"
        
        manga_dirs = [d for d in path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not manga_dirs:
            return False, "No manga folders found"
        
        return True, "Valid path"