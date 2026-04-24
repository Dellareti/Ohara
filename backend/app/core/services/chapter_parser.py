import re
from typing import Dict, List

from app.core.config import CHAPTER_PATTERNS
from app.models.manga import Chapter


class ChapterParser:
    """
    Specialized parser for manga chapter analysis and processing.
    
    Responsible for:
    - Chapter name parsing using regex
    - Extracting chapter and volume numbers
    - Natural chapter sorting
    - Sequential numbering determination
    """
    
    @staticmethod
    def parse_chapter_name_enhanced(chapter_name: str) -> Dict:
        """
        Advanced chapter name parser with support for multiple patterns and languages.

        Automatically detects chapter and volume numbers using optimized regex.

        Args:
            chapter_name (str): Chapter directory name

        Returns:
            Dict: {
                'number': float or None - Detected chapter number
                'volume': int or None - Volume number (if present)
            }

        Supported languages:
            - English: "Chapter 1", "Ch. 1", "Vol. 1 Ch. 15"
            - Portuguese: "Capítulo 1", "Cap. 1", "Tomo 1 Capítulo 2"
            - Spanish: "Capítulo 1", "Cap. 1", "Tomo 1 Capítulo 2"
            - French: "Chapitre 1", "Chap. 1", "Tome 1 Chapitre 2"
            - German: "Kapitel 1", "Kap. 1", "Band 1 Kapitel 2"
            - Italian: "Capitolo 1", "Cap. 1", "Tomo 1 Capitolo 2"
            - Russian: "Глава 1", "Гл. 1", "Том 1 Глава 2"
            - Japanese: "第1話", "第1章", "1話"
            - Chinese: "第1章", "第1回", "第1话"
            - Hindi: "अध्याय 1", "भाग 1"
            - Arabic: "الفصل 1", "فصل 1"
            - Numeric: "001", "1 - Title", "1.5"
        """
        info = {'number': None, 'volume': None}

        enhanced_patterns = [
            # Combined Volume + Chapter
            r'[Vv]ol\.?\s*(\d+)[,]?\s*[Cc]h\.?\s*(\d+\.?\d*)',                  # EN: "Vol. 1, Ch. 15"
            r'Volume\s*(\d+)\s*Chapter\s*(\d+\.?\d*)',                          # EN: "Volume 1 Chapter 1"
            r'[Tt]ome\s*(\d+)\s*[Cc]hap(?:itre)?\.?\s*(\d+\.?\d*)',             # FR: "Tome 1 Chapitre 2"
            r'[Bb]and\s*(\d+)\s*[Kk]ap(?:itel)?\.?\s*(\d+\.?\d*)',              # DE: "Band 1 Kapitel 2"
            r'[Tt]omo\s*(\d+)\s*[Cc]ap(?:[ií]tulo|itolo)?\.?\s*(\d+\.?\d*)',    # PT/ES/IT: "Tomo 1 Capítulo 2"
            r'[Тт]ом\s*(\d+)\s*[Гг]л(?:ава)?\.?\s*(\d+\.?\d*)',                 # RU: "Том 1 Глава 2"
            # Single chapter (long form)
            r'[Cc]hapter\s*(\d+\.?\d*)',                                         # EN: "Chapter 1"
            r'[Cc]ap[ií]tulo\s*(\d+\.?\d*)',                                     # PT/ES: "Capítulo 1"
            r'[Cc]hapitre\s*(\d+\.?\d*)',                                        # FR: "Chapitre 1"
            r'[Kk]apitel\s*(\d+\.?\d*)',                                         # DE: "Kapitel 1"
            r'[Cc]apitolo\s*(\d+\.?\d*)',                                        # IT: "Capitolo 1"
            r'[Гг]лава\s*(\d+\.?\d*)',                                           # RU: "Глава 1"
            r'第\s*(\d+\.?\d*)\s*[話章回话節节]',                                    # JA/ZH: "第1話"
            r'(\d+\.?\d*)\s*[話章回话]',                                           # JA/ZH: "1話"
            r'अध्याय\s*(\d+\.?\d*)',                                             # HI: "अध्याय 1"
            r'भाग\s*(\d+\.?\d*)',                                                 # HI: "भाग 1"
            r'الفصل\s*(\d+\.?\d*)',                                              # AR: "الفصل 1"
            r'فصل\s*(\d+\.?\d*)',                                                # AR: "فصل 1"
            # Short abbreviations
            r'[Cc]hap\.?\s*(\d+\.?\d*)',                                         # FR: "Chap. 1"
            r'[Cc]h\.?\s*(\d+\.?\d*)',                                           # EN: "Ch. 1"
            r'[Cc]ap\.?\s*(\d+\.?\d*)',                                          # PT/ES/IT: "Cap. 1"
            r'[Kk]ap\.?\s*(\d+\.?\d*)',                                          # DE: "Kap. 1"
            r'[Гг]л\.?\s*(\d+\.?\d*)',                                           # RU: "Гл. 1"
            # Numeric fallbacks
            r'^(\d+\.?\d*)(?:\s*[-_].*)?',                                       # "1 - Title"
            r'(\d+\.?\d*)(?:\s|$)',                                              # Loose numbers
        ]

        for pattern in enhanced_patterns:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    try:
                        info['number'] = float(groups[0])
                        break
                    except ValueError:
                        continue
                elif len(groups) == 2:
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                        break
                    except ValueError:
                        continue
        
        return info
    
    @staticmethod
    def parse_chapter_name(chapter_name: str) -> Dict:
        """
        Basic chapter name parser using configuration patterns.
        
        Args:
            chapter_name (str): Chapter name
            
        Returns:
            Dict: Information extracted from the name
        """
        info = {'number': None, 'volume': None}
        
        for pattern in CHAPTER_PATTERNS:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    try:
                        info['number'] = float(groups[0])
                    except ValueError:
                        pass
                elif len(groups) == 2:
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                    except ValueError:
                        pass
                break
        
        return info
    
    @staticmethod
    def sort_chapters(chapters: List[Chapter]) -> List[Chapter]:
        """
        Sorts chapters by number (descending) then by name.
        
        Args:
            chapters (List[Chapter]): List of chapters to sort
            
        Returns:
            List[Chapter]: Sorted list of chapters
        """
        def sort_key(chapter):
            if chapter.number is not None:
                return (0, -chapter.number)
            else:
                return (1, chapter.name)
        
        return sorted(chapters, key=sort_key)
    
    @staticmethod
    def determine_chapter_number(chapter_info: dict, sequential_index: int, 
                               page_count: int, chapter_name: str) -> str:
        """
        Determine chapter number using multiple strategies.
        
        Args:
            chapter_info (dict): Information extracted from parsing
            sequential_index (int): Sequential index of the chapter
            page_count (int): Number of pages in the chapter
            chapter_name (str): Original chapter name
            
        Returns:
            str: Determined chapter number
        """
        if chapter_info['number'] is not None:
            return str(chapter_info['number'])
        
        return str(sequential_index)
    
    @staticmethod
    def natural_sort_key(text: str) -> List:
        """
        Generates a natural sort key for strings containing numbers.
        
        Implements a natural sort algorithm that treats numbers as
        integers instead of strings, ensuring logical order:
        
        Alphabetical sort: ["1", "10", "2", "20"]
        Natural sort:      ["1", "2", "10", "20"]
        
        Args:
            text (str): String to be converted to sort key
            
        Returns:
            List: Mixed list of integers and strings for sorting
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', text)]