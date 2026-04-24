import logging
import urllib.parse
from pathlib import Path

from app.core.library_state import library_state

logger = logging.getLogger(__name__)


def create_image_url(file_path):
    """
    Creates an API URL to serve an image based on the file path.
    
    Args:
        file_path: Absolute path to the image file
    
    Returns:
        str: API URL to access the image, or None if invalid
    """
    
    if not file_path:
        return None
    
    try:
        # Check if it is an image file
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        file_path_obj = Path(file_path)
        
        if file_path_obj.suffix.lower() not in image_extensions:
            logger.warning(f"File is not an image: {file_path}")
            return None
        
        # Check if file exists
        if not file_path_obj.exists():
            logger.warning(f"Image file not found: {file_path}")
            return None
        
        # Check if file is within the library (security)
        if library_state.current_path:
            try:
                library_path = Path(library_state.current_path).resolve()
                file_absolute = file_path_obj.resolve()
                
                # Verify file is inside the library
                try:
                    file_absolute.relative_to(library_path)
                except ValueError:
                    logger.warning(f"File outside library: {file_path}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error checking path security: {e}")
                return None
        
        # Encode path for URL
        encoded_path = urllib.parse.quote(str(file_path_obj), safe='')
        
        return f"/api/image?path={encoded_path}"
        
    except Exception as e:
        logger.warning(f"Error creating image URL for {file_path}: {str(e)}")
        return None