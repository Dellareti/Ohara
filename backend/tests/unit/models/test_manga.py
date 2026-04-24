from datetime import datetime

import pytest

from app.models.manga import Page, Chapter, Manga, Library, LibraryResponse, MangaResponse, ChapterResponse

@pytest.fixture
def single_page():
    return Page(
        filename="page_01.jpg",
        path="/manga/one-piece/ch-1/page_01.jpg",
        size=1024000,
        width=800,
        height=1200
    )


@pytest.fixture
def list_of_pages():
    return [
        Page(filename="01.jpg", path="/ch1/01.jpg", size=500000),
        Page(filename="02.jpg", path="/ch1/02.jpg", size=520000),
        Page(filename="03.jpg", path="/ch1/03.jpg", size=480000)
    ]


@pytest.fixture
def single_chapter(list_of_pages):
    return Chapter(
        id="one-piece-ch-1001",
        name="Chapter 1001",
        number=1001.0,
        volume=100,
        path="/manga/One Piece/Chapter 1001",
        pages=list_of_pages,
        page_count=len(list_of_pages)
    )


@pytest.fixture
def list_of_chapters(list_of_pages):
    chapters = []
    for i in range(1, 4):
        chapter = Chapter(
            id=f"one-piece-ch-{i}",
            name=f"Chapter {i}",
            number=float(i),
            path=f"/manga/One Piece/Chapter {i}",
            pages=list_of_pages[:i],
            page_count=i
        )
        chapters.append(chapter)
    return chapters


@pytest.fixture
def single_manga(list_of_chapters):
    total_pages = sum(ch.page_count for ch in list_of_chapters)
    return Manga(
        id="one-piece",
        title="One Piece",
        path="/manga/One Piece",
        thumbnail="/thumbnails/one-piece.jpg",
        chapters=list_of_chapters,
        chapter_count=len(list_of_chapters),
        total_pages=total_pages,
        author="Eiichiro Oda",
        status="Ongoing",
        genres=["Action", "Adventure", "Shounen"]
    )


@pytest.fixture
def list_of_mangas(single_manga, list_of_chapters):
    manga1 = single_manga

    manga2 = Manga(
        id="naruto",
        title="Naruto",
        path="/manga/Naruto",
        chapters=list_of_chapters[:2],
        chapter_count=2,
        total_pages=3,
        author="Masashi Kishimoto",
        status="Completed"
    )

    return [manga1, manga2]


@pytest.fixture
def library(list_of_mangas):
    library = Library()
    for manga in list_of_mangas:
        library.add_manga(manga)
    return library


class TestPage:
    def test_creation_basic(self):
        page = Page(filename="test.jpg", path="/path/test.jpg")

        assert page.filename == "test.jpg"
        assert page.path == "/path/test.jpg"
        assert page.size is None
        assert page.width is None
        assert page.height is None

    def test_creation_complete(self, single_page):
        assert single_page.filename == "page_01.jpg"
        assert single_page.path == "/manga/one-piece/ch-1/page_01.jpg"
        assert single_page.size == 1024000
        assert single_page.width == 800
        assert single_page.height == 1200

    def test_serialization(self, single_page):
        page_dict = single_page.model_dump()

        assert page_dict["filename"] == "page_01.jpg"
        assert page_dict["size"] == 1024000
        assert "path" in page_dict

        new_page = Page(**page_dict)
        assert new_page.filename == single_page.filename
        assert new_page.size == single_page.size


class TestChapter:
    def test_creation_basic(self):
        chapter = Chapter(
            id="test-ch-1",
            name="Test Chapter",
            path="/test/chapter"
        )

        assert chapter.id == "test-ch-1"
        assert chapter.name == "Test Chapter"
        assert chapter.path == "/test/chapter"
        assert chapter.number is None
        assert chapter.volume is None
        assert chapter.pages == []
        assert chapter.page_count == 0
        assert isinstance(chapter.date_added, datetime)

    def test_creation_complete(self, single_chapter):
        assert single_chapter.id == "one-piece-ch-1001"
        assert single_chapter.name == "Chapter 1001"
        assert single_chapter.number == 1001.0
        assert single_chapter.volume == 100
        assert len(single_chapter.pages) == 3
        assert single_chapter.page_count == 3

    def test_decimal_number(self):
        chapter = Chapter(
            id="test-ch-1.5",
            name="Chapter 1.5",
            path="/test",
            number=1.5
        )

        assert chapter.number == 1.5

    def test_date_added_automatic(self):
        before = datetime.now()
        chapter = Chapter(id="test", name="Test", path="/test")
        after = datetime.now()

        assert before <= chapter.date_added <= after

class TestManga:
    def test_creation_basic(self):
        manga = Manga(
            id="test-manga",
            title="Test Manga",
            path="/manga/test"
        )

        assert manga.id == "test-manga"
        assert manga.title == "Test Manga"
        assert manga.path == "/manga/test"
        assert manga.chapters == []
        assert manga.chapter_count == 0
        assert manga.total_pages == 0
        assert manga.genres == []
        assert isinstance(manga.date_added, datetime)
        assert isinstance(manga.date_modified, datetime)

    def test_creation_complete(self, single_manga):
        assert single_manga.id == "one-piece"
        assert single_manga.title == "One Piece"
        assert single_manga.author == "Eiichiro Oda"
        assert single_manga.status == "Ongoing"
        assert "Action" in single_manga.genres
        assert single_manga.chapter_count == 3
        assert single_manga.total_pages == 6

    def test_optional_fields(self):
        manga = Manga(id="test", title="Test", path="/test")

        assert manga.thumbnail is None
        assert manga.author is None
        assert manga.artist is None
        assert manga.status is None
        assert manga.description is None

    def test_timestamps_automatic(self):
        before = datetime.now()
        manga = Manga(id="test", title="Test", path="/test")
        after = datetime.now()

        assert before <= manga.date_added <= after
        assert before <= manga.date_modified <= after


class TestLibrary:
    def test_creation_empty(self):
        library = Library()

        assert library.mangas == []
        assert library.total_mangas == 0
        assert library.total_chapters == 0
        assert library.total_pages == 0
        assert isinstance(library.last_updated, datetime)

    def test_add_manga(self, single_manga):
        library = Library()
        library.add_manga(single_manga)

        assert len(library.mangas) == 1
        assert library.total_mangas == 1
        assert library.total_chapters == single_manga.chapter_count
        assert library.total_pages == single_manga.total_pages
        assert library.mangas[0].id == single_manga.id

    def test_add_duplicate_manga(self, single_manga):
        library = Library()

        library.add_manga(single_manga)
        assert len(library.mangas) == 1

        modified_manga = Manga(
            id=single_manga.id,
            title="Modified Title",
            path="/different/path",
            chapter_count=10,
            total_pages=100
        )

        library.add_manga(modified_manga)

        assert len(library.mangas) == 1
        assert library.mangas[0].title == "Modified Title"
        assert library.total_chapters == 10
        assert library.total_pages == 100

    def test_remove_existing_manga(self, library):
        initial_count = len(library.mangas)
        manga_id = library.mangas[0].id

        result = library.remove_manga(manga_id)
        assert result is True
        assert len(library.mangas) == initial_count - 1
        assert library.get_manga(manga_id) is None

    def test_remove_manga_nonexistent(self, library):
        initial_count = len(library.mangas)
        result = library.remove_manga("nonexistent-id")

        assert result is False
        assert len(library.mangas) == initial_count

    def test_get_existing_manga(self, library):
        manga_id = library.mangas[0].id
        found_manga = library.get_manga(manga_id)

        assert found_manga is not None
        assert found_manga.id == manga_id

    def test_get_nonexistent_manga(self, library):
        found_manga = library.get_manga("nonexistent-id")
        assert found_manga is None

    def test_search_found(self, library):
        results = library.search("piece")
        assert len(results) >= 1
        assert any(manga.title == "One Piece" for manga in results)

    def test_search_not_found(self, library):
        results = library.search("dragon ball")
        assert len(results) == 0

    def test_search_case_insensitive(self, library):
        results_lower = library.search("one piece")
        results_upper = library.search("ONE PIECE")
        results_mixed = library.search("One Piece")

        assert len(results_lower) == len(results_upper) == len(results_mixed)
        assert len(results_lower) >= 1

    def test_stats_update_automatically(self, single_manga):
        library = Library()
        before_update = library.last_updated

        import time
        time.sleep(0.01)

        library.add_manga(single_manga)

        assert library.total_mangas == 1
        assert library.total_chapters == single_manga.chapter_count
        assert library.total_pages == single_manga.total_pages
        assert library.last_updated > before_update


class TestResponseModels:
    def test_creation(self, library):
        response = LibraryResponse(library=library)

        assert response.library == library
        assert response.message == "Success"

    def test_library_custom_message(self, library):
        response = LibraryResponse(
            library=library,
            message="Library loaded successfully"
        )

        assert response.message == "Library loaded successfully"

    def test_manga_creation(self, single_manga):
        response = MangaResponse(manga=single_manga)

        assert response.manga == single_manga
        assert response.message == "Success"

    def test_chapter_creation(self, single_chapter):
        response = ChapterResponse(chapter=single_chapter)

        assert response.chapter == single_chapter
        assert response.message == "Success"