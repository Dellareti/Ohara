import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class LibraryState:
    """Thread-safe class to manage the global library state"""
    def __init__(self):
        self._current_path: Optional[str] = None
        self._lock = threading.RLock()
        self._library_path_file = "last_library_path.txt"
    
    @property
    def current_path(self) -> Optional[str]:
        with self._lock:
            return self._current_path
    
    @current_path.setter
    def current_path(self, path: Optional[str]) -> None:
        with self._lock:
            self._current_path = path
            if path:
                self._save_to_file(path)
            else:
                self._clear_file()
    
    def load_from_file(self) -> Optional[str]:
        """Loads the library path from file"""
        try:
            if Path(self._library_path_file).exists():
                with open(self._library_path_file, 'r', encoding='utf-8') as f:
                    path = f.read().strip()
                    if path and Path(path).exists():
                        with self._lock:
                            self._current_path = path
                        logger.info(f"Path loaded: {path}")
                        return path
                    else:
                        logger.info(f"Saved path no longer exists: {path}")
        except Exception as e:
            logger.warning(f"Error loading path: {e}")
        return None
    
    def _save_to_file(self, path: str) -> None:
        try:
            with open(self._library_path_file, 'w', encoding='utf-8') as f:
                f.write(path)
            logger.info(f"Path saved: {path}")
        except Exception as e:
            logger.warning(f"Error saving path: {e}")
    
    def _clear_file(self) -> None:
        try:
            if Path(self._library_path_file).exists():
                Path(self._library_path_file).unlink()
                logger.info(f"Path file removed")
        except Exception as e:
            logger.warning(f"Error removing file: {e}")
    
    def clear(self) -> None:
        with self._lock:
            self._current_path = None
            self._clear_file()
    
    def is_configured(self) -> bool:
        with self._lock:
            return self._current_path is not None
    
    def validate_current_path(self) -> bool:
        with self._lock:
            if not self._current_path:
                return False
            return Path(self._current_path).exists()


# Global thread-safe instance
library_state = LibraryState()