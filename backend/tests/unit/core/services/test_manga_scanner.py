import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.core.services.manga_scanner import MangaScanner


class TestMangaScannerSimple:
    """Tests for simplified MangaScanner"""

    def setup_method(self):
        self.scanner = MangaScanner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Should initialize the scanner correctly"""
        assert self.scanner.cache_enabled is True
        assert hasattr(self.scanner, 'cache')
        assert hasattr(self.scanner, 'chapter_parser')

    def test_enable_disable_cache(self):
        """Should enable/disable cache"""
        self.scanner.disable_cache()
        assert self.scanner.cache_enabled is False

        self.scanner.enable_cache()
        assert self.scanner.cache_enabled is True

    def test_scan_library_nonexistent_path(self):
        """Should raise exception for non-existent path"""
        with pytest.raises(ValueError, match="Library not found"):
            self.scanner.scan_library("/nonexistent/path")

    def test_discover_manga_directories(self):
        """Should discover manga directories"""
        (self.temp_dir / "Manga1").mkdir()
        (self.temp_dir / "Manga2").mkdir()
        (self.temp_dir / ".hidden").mkdir()
        (self.temp_dir / "file.txt").write_text("text")

        manga_dirs = self.scanner._discover_manga_directories(self.temp_dir)

        assert len(manga_dirs) == 2
        assert all(d.is_dir() for d in manga_dirs)
        assert not any(d.name.startswith('.') for d in manga_dirs)

    def test_discover_chapter_directories(self):
        """Should discover chapter directories with images"""
        manga_dir = self.temp_dir / "Manga1"
        manga_dir.mkdir()

        ch1_dir = manga_dir / "Chapter 1"
        ch1_dir.mkdir()
        (ch1_dir / "page1.jpg").write_text("fake image")

        ch2_dir = manga_dir / "Chapter 2"
        ch2_dir.mkdir()

        chapter_dirs = self.scanner._discover_chapter_directories(manga_dir)

        assert len(chapter_dirs) == 1
        assert chapter_dirs[0].name == "Chapter 1"

    def test_has_images(self):
        """Should detect presence of images"""
        test_dir = self.temp_dir / "test"
        test_dir.mkdir()

        assert self.scanner._has_images(test_dir) is False

        (test_dir / "image.jpg").write_text("fake image")
        assert self.scanner._has_images(test_dir) is True

    def test_find_image_files(self):
        """Should find image files"""
        test_dir = self.temp_dir / "test"
        test_dir.mkdir()

        (test_dir / "page1.jpg").write_text("fake")
        (test_dir / "page2.png").write_text("fake")
        (test_dir / "text.txt").write_text("fake")

        image_files = self.scanner._find_image_files(test_dir)

        assert len(image_files) == 2
        assert all(f.suffix.lower() in ['.jpg', '.png'] for f in image_files)

    def test_generate_manga_id(self):
        """Should generate readable and consistent IDs"""
        id1 = self.scanner._generate_manga_id("Manga Name")
        id2 = self.scanner._generate_manga_id("Manga Name")
        id3 = self.scanner._generate_manga_id("Different Name")

        assert id1 == id2

        assert id1 != id3

        assert id1 == "manga-name"
        assert id3 == "different-name"

    @patch('app.core.services.manga_scanner.MangaScanner._discover_manga_directories')
    @patch('app.core.services.manga_scanner.MangaScanner.scan_manga')
    def test_scan_library_with_cache_disabled(self, mock_scan_manga, mock_discover):
        """Should scan library without using cache"""
        from app.models.manga import Manga
        from datetime import datetime

        manga_dir = self.temp_dir / "Manga1"
        manga_dir.mkdir()
        mock_discover.return_value = [manga_dir]

        mock_manga = Manga(
            id="manga1",
            title="Test Manga",
            path=str(manga_dir),
            thumbnail=None,
            chapters=[],
            chapter_count=0,
            total_pages=0,
            date_added=datetime.now(),
            date_modified=datetime.now()
        )
        mock_scan_manga.return_value = mock_manga

        self.scanner.disable_cache()

        library = self.scanner.scan_library(str(self.temp_dir))

        assert library.total_mangas == 1
        assert len(library.mangas) == 1
        mock_scan_manga.assert_called_once()

    def test_clear_cache(self):
        """Should clear cache"""
        cache_file = self.temp_dir / self.scanner.cache.cache_file_name
        cache_file.write_text('{"test": "data"}')

        result = self.scanner.clear_cache(str(self.temp_dir))

        assert result is True
        assert not cache_file.exists()

    def test_get_cache_info(self):
        """Should return cache information"""
        info = self.scanner.get_cache_info(str(self.temp_dir))
        assert info["exists"] is False

        cache_file = self.temp_dir / self.scanner.cache.cache_file_name
        cache_file.write_text('{"manga1": {"test": "data"}}')

        info = self.scanner.get_cache_info(str(self.temp_dir))
        assert info["exists"] is True
        assert info["entries"] == 1

    def test_validate_library_path_valid(self):
        """Should validate a valid path"""
        manga_dir = self.temp_dir / "Test Manga"
        manga_dir.mkdir()

        is_valid, message = self.scanner.validate_library_path(str(self.temp_dir))
        assert is_valid is True
        assert message == "Valid path"

    def test_validate_library_path_nonexistent(self):
        """Should reject a non-existent path"""
        is_valid, message = self.scanner.validate_library_path("/nonexistent/path")
        assert is_valid is False
        assert message == "Path does not exist"

    def test_validate_library_path_not_directory(self):
        """Should reject a file instead of a directory"""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test")

        is_valid, message = self.scanner.validate_library_path(str(test_file))
        assert is_valid is False
        assert message == "Path is not a directory"

    def test_validate_library_path_empty(self):
        """Should reject an empty directory"""
        is_valid, message = self.scanner.validate_library_path(str(self.temp_dir))
        assert is_valid is False
        assert message == "No manga folders found"
