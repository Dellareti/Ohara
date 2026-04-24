# backend/app/tests/unit/test_reader_api.py
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.api.endpoints.reader import chapter_to_dict
from app.models.manga import Page, Chapter, Manga

@pytest.fixture
def pages():
    return [
        Page(filename="page_01.jpg", path="/manga/test/ch1/page_01.jpg", size=500000),
        Page(filename="page_02.jpg", path="/manga/test/ch1/page_02.jpg", size=520000),
        Page(filename="page_03.jpg", path="/manga/test/ch1/page_03.jpg", size=480000)
    ]


@pytest.fixture
def chapter(pages):
    return Chapter(
        id="test-manga-ch-78",
        name="Chapter 78: The Final Battle",
        number=78.0,
        volume=8,
        path="/manga/test/chapter-78",
        pages=pages,
        page_count=len(pages),
        date_added=datetime.now()
    )


@pytest.fixture
def chapters():
    chapters = []
    for i in range(75, 81):  # 6 chapters
        chapter = Chapter(
            id=f"test-manga-ch-{i}",
            name=f"Chapter {i}",
            number=float(i),
            path=f"/manga/test/chapter-{i}",
            pages=[],
            page_count=20
        )
        chapters.append(chapter)
    return chapters


@pytest.fixture
def manga(chapters):
    return Manga(
        id="test-manga",
        title="Test Manga",
        path="/manga/test",
        chapters=chapters,
        chapter_count=len(chapters),
        total_pages=sum(ch.page_count for ch in chapters)
    )


@pytest.fixture
def mock_library_state():
    with patch('app.core.library_state.library_state') as mock_state:
        mock_state.current_path = "/mock/library/path"
        yield mock_state


@pytest.fixture
def mock_scanner():
    with patch('app.core.services.manga_scanner') as mock_scanner:
        yield mock_scanner


class TestChapterToDict:
    def test_complete_data(self, chapter):
        result = chapter_to_dict(chapter)

        assert result["id"] == chapter.id
        assert result["name"] == chapter.name
        assert result["number"] == chapter.number
        assert result["volume"] == chapter.volume
        assert result["path"] == chapter.path
        assert result["page_count"] == chapter.page_count

        assert "date_added" in result
        assert isinstance(result["date_added"], str)  # ISO format

        assert len(result["pages"]) == len(chapter.pages)
        assert isinstance(result["pages"], list)

    def test_pages_structure(self, chapter):
        result = chapter_to_dict(chapter)

        first_page = result["pages"][0]
        expected_keys = ["filename", "path", "size", "width", "height"]

        for key in expected_keys:
            assert key in first_page

        assert first_page["filename"] == chapter.pages[0].filename
        assert first_page["path"] == chapter.pages[0].path
        assert first_page["size"] == chapter.pages[0].size

    def test_minimal_data(self):
        minimal_chapter = Chapter(
            id="minimal-ch",
            name="Minimal Chapter",
            path="/minimal"
        )

        result = chapter_to_dict(minimal_chapter)

        assert result["id"] == "minimal-ch"
        assert result["name"] == "Minimal Chapter"
        assert result["number"] is None
        assert result["volume"] is None
        assert result["pages"] == []
        assert result["page_count"] == 0

    def test_no_date(self):
        chapter = Chapter(
            id="no-date",
            name="No Date Chapter",
            path="/test"
        )
        chapter.date_added = None

        result = chapter_to_dict(chapter)

        assert result["date_added"] is None

    def test_empty_pages(self):
        chapter = Chapter(
            id="empty-pages",
            name="Empty Pages Chapter",
            path="/test",
            pages=[],
            page_count=0
        )

        result = chapter_to_dict(chapter)

        assert result["pages"] == []
        assert result["page_count"] == 0

    def test_datetime_serialization(self, chapter):
        result = chapter_to_dict(chapter)
        assert isinstance(result["date_added"], str)

        parsed_date = datetime.fromisoformat(result["date_added"].replace('Z', '+00:00'))
        assert isinstance(parsed_date, datetime)


class TestEndpoint:
    @pytest.mark.asyncio
    async def test_get_chapter_no_library_configured(self, mock_library_state):
        mock_library_state.current_path = None

        from app.api.endpoints.reader import get_chapter

        with pytest.raises(HTTPException) as exc_info:
            await get_chapter("test-manga", "test-chapter")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "No library configured"

    @pytest.mark.asyncio
    async def test_get_manga_chapters_no_library_configured(self, mock_library_state):
        mock_library_state.current_path = None

        from app.api.endpoints.reader import get_manga_chapters

        with pytest.raises(HTTPException) as exc_info:
            await get_manga_chapters("test-manga")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "No library configured"

    @pytest.mark.asyncio
    async def test_save_reading_progress_valid_data(self):
        from app.api.endpoints.reader import save_reading_progress

        with patch('builtins.open', create=True):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('json.dump'):
                    result = await save_reading_progress(
                        manga_id="test-manga",
                        chapter_id="test-chapter",
                        current_page=5,
                        total_pages=20,
                        reading_time_seconds=300
                    )

                    assert "message" in result
                    assert result["message"] == "Progress saved successfully"

                    assert "progress" in result
                    progress = result["progress"]
                    assert progress["current_page"] == 5
                    assert progress["total_pages"] == 20
                    assert progress["reading_time_seconds"] == 300
                    assert "progress_percentage" in progress
                    assert "is_completed" in progress
                    assert "last_read" in progress

    @pytest.mark.asyncio
    async def test_save_reading_progress_completion(self):
        from app.api.endpoints.reader import save_reading_progress

        with patch('builtins.open', create=True):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('json.dump'):
                    result = await save_reading_progress(
                        manga_id="test-manga",
                        chapter_id="test-chapter",
                        current_page=19,  # Last page
                        total_pages=20
                    )

                    progress = result["progress"]
                    assert progress["current_page"] == 19
                    assert progress["total_pages"] == 20
                    assert progress["is_completed"] is True
                    assert progress["progress_percentage"] == 100.0

    @pytest.mark.asyncio
    async def test_get_manga_progress_no_file(self):
        from app.api.endpoints.reader import get_manga_progress

        with patch('pathlib.Path.exists', return_value=False):
            result = await get_manga_progress("test-manga")

            assert result["manga_id"] == "test-manga"
            assert result["chapters"] == {}
            assert result["manga_info"] == {}
            assert result["message"] == "No progress found"

    @pytest.mark.asyncio
    async def test_get_manga_progress_existing_file(self):
        from app.api.endpoints.reader import get_manga_progress

        mock_progress_data = {
            "test-manga": {
                "chapter-1": {
                    "current_page": 5,
                    "total_pages": 20,
                    "progress_percentage": 25.0,
                    "is_completed": False
                },
                "_manga_info": {
                    "last_chapter_read": "chapter-1",
                    "total_reading_time": 600
                }
            }
        }

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_progress_data):
                    result = await get_manga_progress("test-manga")

                    assert result["manga_id"] == "test-manga"
                    assert "chapter-1" in result["chapters"]
                    assert result["chapters"]["chapter-1"]["current_page"] == 5
                    assert result["manga_info"]["last_chapter_read"] == "chapter-1"

    @pytest.mark.asyncio
    async def test_get_chapter_progress_not_found(self):
        from app.api.endpoints.reader import get_chapter_progress

        with patch('pathlib.Path.exists', return_value=False):
            result = await get_chapter_progress("test-manga", "test-chapter")

            assert result["manga_id"] == "test-manga"
            assert result["chapter_id"] == "test-chapter"
            assert result["progress"] is None
            assert result["message"] == "No progress found"

    @pytest.mark.asyncio
    async def test_get_chapter_progress_found(self):
        from app.api.endpoints.reader import get_chapter_progress

        mock_progress_data = {
            "test-manga": {
                "test-chapter": {
                    "current_page": 10,
                    "total_pages": 20,
                    "progress_percentage": 52.63,
                    "is_completed": False,
                    "last_read": "2025-01-01T12:00:00"
                }
            }
        }

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_progress_data):
                    result = await get_chapter_progress("test-manga", "test-chapter")

                    assert result["manga_id"] == "test-manga"
                    assert result["chapter_id"] == "test-chapter"
                    assert result["progress"]["current_page"] == 10
                    assert result["progress"]["total_pages"] == 20
                    assert result["progress"]["is_completed"] is False

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_save_progress_file_error(self):
        from app.api.endpoints.reader import save_reading_progress

        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(HTTPException) as exc_info:
                await save_reading_progress("test", "test", 1, 10)

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "Error saving progress: Permission denied"

    @pytest.mark.asyncio
    async def test_get_progress_file_error(self):
        from app.api.endpoints.reader import get_manga_progress

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("Read error")):
                with pytest.raises(HTTPException) as exc_info:
                    await get_manga_progress("test-manga")

                assert exc_info.value.status_code == 500
                assert exc_info.value.detail == "Error loading progress: Read error"

    def test_invalid_input(self):
        with pytest.raises(AttributeError):
            chapter_to_dict(None)