"""
Optional OCR functionality using pytesseract.
"""
from typing import List, Optional
import io
from collections import Counter
import re

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def is_ocr_available() -> bool:
    """Check if OCR functionality is available."""
    if not TESSERACT_AVAILABLE:
        return False
    
    try:
        # Try to run tesseract to verify it's installed
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_tokens(image_bytes: bytes, top_n: int = 5) -> List[str]:
    """
    Extract text tokens from an image using OCR.
    
    Args:
        image_bytes: Raw image bytes
        top_n: Number of top frequent tokens to return
        
    Returns:
        List of text tokens found in the image
    """
    if not is_ocr_available():
        return []
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale for better OCR
        image = image.convert('L')
        
        # Downscale if too large (for performance)
        max_dimension = 1200
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Run OCR
        text = pytesseract.image_to_string(image)
        
        # Extract meaningful tokens
        # Remove short words, numbers only, and common stop words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Simple stop words list
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
            'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get',
            'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
            'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let',
            'put', 'say', 'she', 'too', 'use'
        }
        
        # Filter out stop words
        words = [w for w in words if w not in stop_words]
        
        if not words:
            return []
        
        # Get most common tokens
        counter = Counter(words)
        top_tokens = [word for word, count in counter.most_common(top_n)]
        
        return top_tokens
        
    except Exception as e:
        # Silently fail and return empty list
        return []


def format_tokens_for_prompt(tokens: List[str]) -> str:
    """
    Format OCR tokens for inclusion in the AI prompt.
    
    Args:
        tokens: List of extracted text tokens
        
    Returns:
        Formatted string for prompt
    """
    if not tokens:
        return "None"
    
    return ", ".join(tokens)

