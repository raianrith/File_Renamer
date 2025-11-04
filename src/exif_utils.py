"""
EXIF data extraction and date handling utilities.
"""
from typing import Optional, Dict, Any, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import io


def extract_exif(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract EXIF data from image bytes.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Dictionary of EXIF data with human-readable tags
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = {}
        
        # Get EXIF data
        exif = image._getexif()
        if exif is not None:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
        
        return exif_data
    except Exception as e:
        return {"error": str(e)}


def get_exif_date(exif_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract the capture date from EXIF data.
    
    Args:
        exif_data: Dictionary of EXIF data
        
    Returns:
        Date string in YYYYMMDD format, or None if not available
    """
    # Try multiple date fields in order of preference
    date_fields = [
        'DateTimeOriginal',
        'DateTime',
        'DateTimeDigitized'
    ]
    
    for field in date_fields:
        if field in exif_data:
            date_str = str(exif_data[field])
            try:
                # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                return dt.strftime("%Y%m%d")
            except ValueError:
                try:
                    # Try alternative format
                    dt = datetime.strptime(date_str[:10], "%Y:%m:%d")
                    return dt.strftime("%Y%m%d")
                except ValueError:
                    continue
    
    return None


def format_exif_summary(exif_data: Dict[str, Any]) -> str:
    """
    Format EXIF data into a human-readable summary.
    
    Args:
        exif_data: Dictionary of EXIF data
        
    Returns:
        Formatted string summary
    """
    if not exif_data or "error" in exif_data:
        return "No EXIF data available"
    
    summary_fields = [
        ('Make', 'Camera Make'),
        ('Model', 'Camera Model'),
        ('DateTimeOriginal', 'Date Taken'),
        ('ExposureTime', 'Exposure Time'),
        ('FNumber', 'F-Number'),
        ('ISOSpeedRatings', 'ISO'),
        ('FocalLength', 'Focal Length'),
        ('Flash', 'Flash'),
        ('ImageWidth', 'Width'),
        ('ImageHeight', 'Height'),
    ]
    
    lines = []
    for key, label in summary_fields:
        if key in exif_data:
            value = exif_data[key]
            # Format certain values
            if key == 'ExposureTime':
                if isinstance(value, tuple) and len(value) == 2:
                    value = f"{value[0]}/{value[1]}s"
            elif key == 'FNumber':
                if isinstance(value, tuple) and len(value) == 2:
                    value = f"f/{value[0]/value[1]:.1f}"
            elif key == 'FocalLength':
                if isinstance(value, tuple) and len(value) == 2:
                    value = f"{value[0]/value[1]:.1f}mm"
            
            lines.append(f"{label}: {value}")
    
    return "\n".join(lines) if lines else "Limited EXIF data"


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get image width and height.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (width, height)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return image.size
    except Exception:
        return (0, 0)


def create_thumbnail(image_bytes: bytes, max_size: Tuple[int, int] = (200, 200)) -> bytes:
    """
    Create a thumbnail from image bytes.
    
    Args:
        image_bytes: Raw image bytes
        max_size: Maximum thumbnail size (width, height)
        
    Returns:
        Thumbnail image bytes
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception:
        return image_bytes

