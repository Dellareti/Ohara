import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.services.simple_cache import SimpleCache
from app.models.manga import Chapter, Manga


class TestSimpleCache:
    """Tests for SimpleCache"""

    def setup_method(self):
        self.cache = SimpleCache()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_file = self.temp_dir / self.cache.cache_file_name

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_cache_nonexistent_file(self):
        """Should return empty dict for non-existent file"""
        result = self.cache.load_cache(self.temp_dir / "nonexistent.json")
        assert result == {}

    def test_load_cache_valid_cache(self):
        """Should load valid cache"""
        cache_data = {"manga1": {"manga_data": {"title": "Test"}, "dir_mtime": 123456}}
        self.cache_file.write_text(json.dumps(cache_data))

        result = self.cache.load_cache(self.cache_file)
        assert result == cache_data

    def test_load_cache_invalid_json(self):
        """Should return empty dict for invalid JSON"""
        self.cache_file.write_text("invalid json")

        result = self.cache.load_cache(self.cache_file)
        assert result == {}

    def test_save_cache(self):
        """Should save cache correctly"""
        chapter = Chapter(
            id="ch1",
            name="Chapter 1",
            number=1,
            path=str(self.temp_dir / "manga1" / "ch1"),
            page_count=10,
            date_added=datetime.now()
        )

        manga = Manga(
            id="manga1",
            title="Test Manga",
            path=str(self.temp_dir / "manga1"),
            thumbnail="thumb.jpg",
            chapters=[chapter],
            chapter_count=1,
            total_pages=10,
            date_added=datetime.now(),
            date_modified=datetime.now()
        )

        manga_dir = Path(manga.path)
        manga_dir.mkdir(parents=True, exist_ok=True)

        self.cache.save_cache(self.cache_file, [manga])

        assert self.cache_file.exists()

        cache_data = json.loads(self.cache_file.read_text())
        assert "manga1" in cache_data
        assert cache_data["manga1"]["manga_data"]["title"] == "Test Manga"
        assert "dir_mtime" in cache_data["manga1"]

    def test_is_valid_no_cache_entry(self):
        """Should return False for nonexistent entry"""
        manga_dir = self.temp_dir / "manga1"
        manga_dir.mkdir()

        result = self.cache.is_valid(manga_dir, None)
        assert result is False

    def test_is_valid_valid_cache(self):
        """Should return True for valid cache"""
        manga_dir = self.temp_dir / "manga1"
        manga_dir.mkdir()

        dir_mtime = manga_dir.stat().st_mtime
        cache_entry = {"dir_mtime": dir_mtime}

        result = self.cache.is_valid(manga_dir, cache_entry)
        assert result is True

    def test_is_valid_outdated_cache(self):
        """Should return False for outdated cache"""
        manga_dir = self.temp_dir / "manga1"
        manga_dir.mkdir()

        cache_entry = {"dir_mtime": 0}

        result = self.cache.is_valid(manga_dir, cache_entry)
        assert result is False

    def test_restore_manga_valid_data(self):
        """Should restore manga with valid data"""
        manga_data = {
            "id": "manga1",
            "title": "Test Manga",
            "path": "/test/path",
            "thumbnail": "thumb.jpg",
            "chapters": [],
            "chapter_count": 0,
            "total_pages": 0,
            "date_added": datetime.now().isoformat(),
            "date_modified": datetime.now().isoformat()
        }

        manga = self.cache.restore_manga(manga_data)
        assert manga is not None
        assert manga.title == "Test Manga"
        assert manga.id == "manga1"

    def test_restore_manga_invalid_data(self):
        """Should return None for invalid data"""
        invalid_data = {"invalid": "data"}

        manga = self.cache.restore_manga(invalid_data)
        assert manga is None

    def test_clear_cache_existing_file(self):
        """Should clear existing cache"""
        self.cache_file.write_text("{}")

        result = self.cache.clear_cache(str(self.temp_dir))
        assert result is True
        assert not self.cache_file.exists()

    def test_clear_cache_nonexistent_file(self):
        """Should return False for non-existent file"""
        result = self.cache.clear_cache(str(self.temp_dir))
        assert result is False

    def test_get_cache_info_existing_cache(self):
        """Should return existing cache information"""
        cache_data = {"manga1": {"test": "data"}}
        self.cache_file.write_text(json.dumps(cache_data))

        info = self.cache.get_cache_info(str(self.temp_dir))

        assert info["exists"] is True
        assert info["entries"] == 1
        assert "size_mb" in info

    def test_get_cache_info_nonexistent_cache(self):
        """Should return correct information for non-existent cache"""
        info = self.cache.get_cache_info(str(self.temp_dir))

        assert info["exists"] is False
