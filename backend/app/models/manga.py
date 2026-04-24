from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

class Page(BaseModel):
    filename: str
    path: str
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class Chapter(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "one-piece-ch-1001",
                "name": "Chapter 1001",
                "number": 1001,
                "volume": 100,
                "path": "/path/to/manga/One Piece/Chapter 1001",
                "page_count": 19,
                "pages": []
            }
        }
    )

    id: str = Field(..., description="Unique chapter ID")
    name: str = Field(..., description="Chapter name")
    number: Optional[float] = Field(None, description="Chapter number")
    volume: Optional[int] = Field(None, description="Volume number")
    path: str = Field(..., description="Chapter folder path")
    pages: List[Page] = Field(default_factory=list, description="List of pages")
    page_count: int = Field(0, description="Total number of pages")
    date_added: datetime = Field(default_factory=datetime.now)

class Manga(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "one-piece",
                "title": "One Piece",
                "path": "/path/to/manga/One Piece",
                "thumbnail": "/static/thumbnails/one-piece.jpg",
                "chapter_count": 1050,
                "total_pages": 20000,
                "author": "Eiichiro Oda",
                "status": "Ongoing",
                "genres": ["Action", "Adventure", "Shounen"]
            }
        }
    )
    
    id: str = Field(..., description="Unique manga ID")
    title: str = Field(..., description="Manga title")
    path: str = Field(..., description="Manga folder path")
    thumbnail: Optional[str] = Field(None, description="Thumbnail path")
    chapters: List[Chapter] = Field(default_factory=list, description="List of chapters")
    chapter_count: int = Field(0, description="Total number of chapters")
    total_pages: int = Field(0, description="Total number of pages")

    author: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    description: Optional[str] = None

    date_added: datetime = Field(default_factory=datetime.now)
    date_modified: datetime = Field(default_factory=datetime.now)

class Library(BaseModel):
    mangas: List[Manga] = Field(default_factory=list)
    total_mangas: int = Field(0, description="Total manga in the library")
    total_chapters: int = Field(0, description="Total chapters")
    total_pages: int = Field(0, description="Total pages")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def add_manga(self, manga: Manga) -> None:
        existing = next((m for m in self.mangas if m.id == manga.id), None)
        if existing:
            self.mangas.remove(existing)
        
        self.mangas.append(manga)
        self._update_stats()
    
    def remove_manga(self, manga_id: str) -> bool:
        manga = next((m for m in self.mangas if m.id == manga_id), None)
        if manga:
            self.mangas.remove(manga)
            self._update_stats()
            return True
        return False
    
    def get_manga(self, manga_id: str) -> Optional[Manga]:
        return next((m for m in self.mangas if m.id == manga_id), None)
    
    def search(self, query: str) -> List[Manga]:
        query = query.lower()
        return [m for m in self.mangas if query in m.title.lower()]
    
    def _update_stats(self) -> None:
        self.total_mangas = len(self.mangas)
        self.total_chapters = sum(m.chapter_count for m in self.mangas)
        self.total_pages = sum(m.total_pages for m in self.mangas)
        self.last_updated = datetime.now()

# API Request/Response Models
class LibraryResponse(BaseModel):
    library: Library
    message: str = "Success"

class MangaResponse(BaseModel):
    manga: Manga
    message: str = "Success"

class ChapterResponse(BaseModel):
    chapter: Chapter
    message: str = "Success"