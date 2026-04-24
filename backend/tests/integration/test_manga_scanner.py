from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.core.services.manga_scanner import MangaScanner
from app.main import app


class TestMangaScanner:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def library(self):
        with TemporaryDirectory() as temp_dir:
            structure = {
                "One Piece": {
                    "Chapter 1095 - The World That Should Be": ["01.jpg", "02.jpg", "03.jpg"],
                    "Chapter 1094": ["page1.png", "page2.png"],
                    "Cap 1093 - Luffy's Dream": ["1.jpeg", "2.jpeg", "3.jpeg", "4.jpeg"]
                },
                "Attack on Titan": {
                    "Vol. 34 Ch. 139 - Final": ["p01.jpg", "p02.jpg"],
                    "139": ["scan_01.png", "scan_02.png", "scan_03.png"],
                    "Chapter 138": ["01.webp", "02.webp"]
                },
                "Solo Leveling": {
                    "001": ["img_001.jpg", "img_002.jpg"],
                    "Ch. 2 - The Weakest Hunter": ["01.png", "02.png", "03.png"],
                    "Capítulo 003": ["page01.jpg", "page02.jpg"]
                }
            }

            for manga_name, chapters in structure.items():
                manga_path = Path(temp_dir) / manga_name

                for chapter_name, pages in chapters.items():
                    chapter_path = manga_path / chapter_name
                    chapter_path.mkdir(parents=True)

                    for page_name in pages:
                        img = Image.new('RGB', (200, 300), color=(
                            hash(page_name) % 255,
                            hash(chapter_name) % 255,
                            hash(manga_name) % 255
                        ))
                        img.save(chapter_path / page_name, quality=85)

            yield temp_dir

    def test_complete_library_scan(self, library):
        scanner = MangaScanner()
        library = scanner.scan_library(library)

        assert library.total_mangas == 3
        assert len(library.mangas) == 3

        one_piece = library.get_manga("one-piece")
        aot = library.get_manga("attack-on-titan")
        solo = library.get_manga("solo-leveling")

        assert one_piece is not None
        assert one_piece.chapter_count == 3

        assert aot is not None
        assert aot.chapter_count == 3

        assert solo is not None
        assert solo.chapter_count == 3

        assert one_piece.chapters[0].number == 1095
        assert one_piece.chapters[-1].number == 1093

        total_pages = sum(manga.total_pages for manga in library.mangas)
        assert total_pages == 23

    def test_api_filesystem(self, client, library):
        scanner = MangaScanner()
        library = scanner.scan_library(library)

        api_response = {
            "mangas": [
                {
                    "id": manga.id,
                    "title": manga.title,
                    "chapter_count": manga.chapter_count,
                    "total_pages": manga.total_pages,
                    "thumbnail": manga.thumbnail,
                    "chapters": [
                        {
                            "id": ch.id,
                            "name": ch.name,
                            "number": ch.number,
                            "page_count": ch.page_count
                        } for ch in manga.chapters[:5]
                    ]
                } for manga in library.mangas
            ],
            "total_mangas": library.total_mangas,
            "total_chapters": library.total_chapters,
            "total_pages": library.total_pages
        }

        assert len(api_response["mangas"]) == 3
        assert api_response["total_mangas"] == 3
        assert api_response["total_pages"] == 23

        for manga_data in api_response["mangas"]:
            assert "id" in manga_data
            assert "title" in manga_data
            assert manga_data["chapter_count"] == 3
            assert len(manga_data["chapters"]) == 3

            if len(manga_data["chapters"]) > 1:
                first_chapter = manga_data["chapters"][0].get("number", 0)
                second_chapter = manga_data["chapters"][1].get("number", 0)
                if first_chapter and second_chapter:
                    assert first_chapter >= second_chapter

    def test_chapter_parsing(self, library):
        scanner = MangaScanner()
        library = scanner.scan_library(library)

        one_piece = library.get_manga("one-piece")

        chapter_tests = {
            "Chapter 1095 - The World That Should Be": 1095,
            "Chapter 1094": 1094,
            "Cap 1093 - Luffy's Dream": 1093
        }

        for chapter in one_piece.chapters:
            expected_number = chapter_tests.get(chapter.name)
            if expected_number:
                assert chapter.number == expected_number

        aot = library.get_manga("attack-on-titan")

        ch139_count = sum(1 for ch in aot.chapters if ch.number == 139)
        assert ch139_count >= 1

        vol_chapter = next((ch for ch in aot.chapters if "Vol." in ch.name), None)
        if vol_chapter:
            assert vol_chapter.volume == 34
            assert vol_chapter.number == 139

    def test_thumbnail_generation(self, library):
        scanner = MangaScanner()
        scanned_library = scanner.scan_library(library)

        for manga in scanned_library.mangas:
            assert manga.thumbnail, f"Manga '{manga.title}' has no thumbnail"

            thumbnail_path = Path(manga.thumbnail)
            assert thumbnail_path.exists(), f"Thumbnail '{thumbnail_path}' does not exist"
            assert thumbnail_path.is_file(), f"Thumbnail '{thumbnail_path}' is not a file"
            assert thumbnail_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp'], \
                f"Invalid extension: {thumbnail_path.suffix} for '{manga.title}'"

            try:
                with Image.open(thumbnail_path) as img:
                    img.verify()
            except Exception as e:
                pytest.fail(f"Thumbnail of '{manga.title}' is not a valid image: {e}")

            if manga.chapters and manga.chapters[0].pages:
                expected_first_page = manga.chapters[0].pages[0].path
                thumbnail_parent = Path(manga.thumbnail).parent
                manga_root = Path(manga.path)

                chapter_paths = [Path(ch.path) for ch in manga.chapters]

                assert (
                        manga.thumbnail == expected_first_page
                        or thumbnail_parent == manga_root
                        or thumbnail_parent in chapter_paths
                ), f"Thumbnail of '{manga.title}' is neither the first page nor in the root or a chapter of the manga"

    def test_scan_library_non_existent_path(self):
        scanner = MangaScanner()

        with pytest.raises(ValueError, match="Library not found: /folder/that/does/not/exist"):
            scanner.scan_library("/folder/that/does/not/exist")

    def test_scan_library_empty_path(self):
        scanner = MangaScanner()

        with TemporaryDirectory() as empty_dir:
            library = scanner.scan_library(empty_dir)
            assert library.total_mangas == 0
            assert len(library.mangas) == 0

    def test_scan_library_invalid_archive(self):
        scanner = MangaScanner()

        with TemporaryDirectory() as invalid_dir:
            manga_dir = Path(invalid_dir) / "Fake Manga" / "Chapter 1"
            manga_dir.mkdir(parents=True)
            (manga_dir / "readme.txt").write_text("Not an image")
            (manga_dir / "script.py").write_text("print('hello')")

            library = scanner.scan_library(invalid_dir)
            fake_manga = library.get_manga("fake-manga")

            assert fake_manga is None or fake_manga.chapter_count == 0