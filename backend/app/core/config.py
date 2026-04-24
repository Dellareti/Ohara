from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # General settings
    app_name: str = "Ohara"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API settings
    api_prefix: str = "/api"
    host: str = "localhost"
    port: int = 8000
    
    # CORS settings
    allowed_origins: List[str] = Field(default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ])
    
    # File settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_image_formats: List[str] = Field(default=[".jpg", ".jpeg", ".png", ".gif", ".webp"])
    supported_archive_formats: List[str] = Field(default=[".zip", ".rar", ".cbz", ".cbr"])
    
    # Thumbnail settings
    thumbnail_size: tuple = (300, 400)
    thumbnail_quality: int = 85
    
    # Cache settings
    cache_thumbnails: bool = True
    cache_dir: str = "cache"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "ohara.log"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

# Global settings singleton
_settings = None

def get_settings() -> Settings:
    """Returns the settings singleton instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Useful constants
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
CHAPTER_PATTERNS = [
    # Combined Volume + Chapter
    r'Vol\.\s*\d+,\s*Ch\.\s*(\d+\.?\d*)',                                        # EN: "Vol. 1, Ch. 1.5"
    r'Volume\s*\d+\s*Chapter\s*(\d+\.?\d*)',                                     # EN: "Volume 1 Chapter 1"
    r'[Vv]ol\.?\s*(\d+)\s*[Cc]h\.?\s*(\d+\.?\d*)',                              # EN: "Vol 1 Ch 2"
    r'[Tt]ome\s*(\d+)\s*[Cc]hap(?:itre)?\.?\s*(\d+\.?\d*)',                     # FR: "Tome 1 Chapitre 2"
    r'[Bb]and\s*(\d+)\s*[Kk]ap(?:itel)?\.?\s*(\d+\.?\d*)',                      # DE: "Band 1 Kapitel 2"
    r'[Tt]omo\s*(\d+)\s*[Cc]ap(?:[ií]tulo|itolo)?\.?\s*(\d+\.?\d*)',            # PT/ES/IT: "Tomo 1 Capítulo 2"
    r'[Тт]ом\s*(\d+)\s*[Гг]л(?:ава)?\.?\s*(\d+\.?\d*)',                         # RU: "Том 1 Глава 2"
    # Single chapter (long form)
    r'[Cc]hapter\s*(\d+\.?\d*)',                                                 # EN: "Chapter 1"
    r'[Cc]ap[ií]tulo\s*(\d+\.?\d*)',                                             # PT/ES: "Capítulo 1"
    r'[Cc]hapitre\s*(\d+\.?\d*)',                                                # FR: "Chapitre 1"
    r'[Kk]apitel\s*(\d+\.?\d*)',                                                 # DE: "Kapitel 1"
    r'[Cc]apitolo\s*(\d+\.?\d*)',                                                # IT: "Capitolo 1"
    r'[Гг]лава\s*(\d+\.?\d*)',                                                   # RU: "Глава 1"
    r'第\s*(\d+\.?\d*)\s*[話章回话節节]',                                            # JA/ZH: "第1話", "第1章"
    r'(\d+\.?\d*)\s*[話章回话]',                                                   # JA/ZH: "1話" (no prefix)
    r'अध्याय\s*(\d+\.?\d*)',                                                     # HI: "अध्याय 1"
    r'भाग\s*(\d+\.?\d*)',                                                         # HI: "भाग 1"
    r'الفصل\s*(\d+\.?\d*)',                                                      # AR: "الفصل 1"
    r'فصل\s*(\d+\.?\d*)',                                                        # AR: "فصل 1"
    # Short abbreviations
    r'[Cc]hap\.?\s*(\d+\.?\d*)',                                                 # FR: "Chap. 1"
    r'[Cc]h\.?\s*(\d+\.?\d*)',                                                   # EN: "Ch. 1" or "Ch 1"
    r'[Cc]ap\.?\s*(\d+\.?\d*)',                                                  # PT/ES/IT: "Cap. 1"
    r'[Kk]ap\.?\s*(\d+\.?\d*)',                                                  # DE: "Kap. 1"
    r'[Гг]л\.?\s*(\d+\.?\d*)',                                                   # RU: "Гл. 1"
    # Numeric fallbacks
    r'^(\d+\.?\d*)(?:\s*[-_].*)?',                                               # "1 - Title" or "1_title"
    r'(\d+\.?\d*)(?:\s|$)',                                                      # Decimal numbers like "1.5"
]

# Thumbnail filenames recognized in the manga root folder (case-insensitive match handled by code)
THUMBNAIL_FILENAMES = [
    'cover', 'thumb', 'thumbnail',  # EN
    'capa',                          # PT
    'portada',                       # ES
    'couverture',                    # FR
    'umschlag',                      # DE
    'copertina',                     # IT
    'обложка',                       # RU
    '表紙',                           # JA
    '封面',                           # ZH
    'आवरण',                          # HI
    'غلاف',                          # AR
]