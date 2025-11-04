"""
Filename sanitization, casing conversion, and uniqueness handling.
"""
import re
from typing import List, Dict, Set, Tuple
from slugify import slugify


def sanitize_filename(name: str, max_length: int = 60) -> str:
    """
    Sanitize a filename to contain only safe characters.
    
    Args:
        name: The filename to sanitize (without extension)
        max_length: Maximum length of the filename
        
    Returns:
        Sanitized filename string
    """
    # Remove any extension if present
    name = name.rsplit('.', 1)[0] if '.' in name else name
    
    # Use slugify to handle most special characters
    sanitized = slugify(name, separator='_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "unnamed"
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove trailing hyphens or underscores
    sanitized = sanitized.rstrip('-_')
    
    return sanitized


def apply_casing(name: str, casing: str) -> str:
    """
    Apply the specified casing style to a filename.
    
    Args:
        name: The filename string
        casing: One of 'kebab', 'snake', 'camel', 'title'
        
    Returns:
        Filename with applied casing
    """
    if casing == "kebab":
        # Convert to kebab-case
        name = name.replace('_', '-').replace(' ', '-')
        name = re.sub(r'([A-Z])', r'-\1', name).lower()
        name = re.sub(r'-+', '-', name).strip('-')
        return name
    
    elif casing == "snake":
        # Convert to snake_case
        name = name.replace('-', '_').replace(' ', '_')
        name = re.sub(r'([A-Z])', r'_\1', name).lower()
        name = re.sub(r'_+', '_', name).strip('_')
        return name
    
    elif casing == "camel":
        # Convert to camelCase
        parts = re.split(r'[-_\s]+', name)
        if not parts:
            return name
        result = parts[0].lower()
        for part in parts[1:]:
            if part:
                result += part.capitalize()
        return result
    
    elif casing == "title":
        # Convert to Title Case
        name = name.replace('-', ' ').replace('_', ' ')
        name = ' '.join(word.capitalize() for word in name.split())
        return name
    
    else:
        return name


def ensure_uniqueness(filenames: List[str], extensions: List[str]) -> List[str]:
    """
    Ensure all filenames are unique by appending numeric suffixes if needed.
    
    Args:
        filenames: List of filenames (without extensions)
        extensions: Corresponding list of file extensions (including dot)
        
    Returns:
        List of unique filenames with extensions
    """
    seen: Dict[str, int] = {}
    result: List[str] = []
    
    for name, ext in zip(filenames, extensions):
        if not name:
            name = "unnamed"
        
        full_name = f"{name}{ext}"
        
        if full_name.lower() not in seen:
            seen[full_name.lower()] = 1
            result.append(full_name)
        else:
            # Append numeric suffix
            counter = seen[full_name.lower()]
            while True:
                new_full_name = f"{name}-{counter}{ext}"
                if new_full_name.lower() not in seen:
                    seen[new_full_name.lower()] = 1
                    result.append(new_full_name)
                    break
                counter += 1
            seen[full_name.lower()] = counter + 1
    
    return result


def validate_filename(name: str, max_length: int = 60) -> Tuple[bool, str]:
    """
    Validate a filename and return validation status.
    
    Args:
        name: Filename to validate (without extension)
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or name.strip() == "":
        return False, "Filename cannot be empty"
    
    if len(name) > max_length:
        return False, f"Filename exceeds maximum length of {max_length}"
    
    # Check for illegal characters
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    if re.search(illegal_chars, name):
        return False, "Filename contains illegal characters"
    
    # Check if it starts or ends with a dot
    if name.startswith('.') or name.endswith('.'):
        return False, "Filename cannot start or end with a dot"
    
    return True, ""


def add_exif_prefix(name: str, exif_date: str) -> str:
    """
    Add EXIF date prefix to filename.
    
    Args:
        name: The filename
        exif_date: Date string in YYYYMMDD format
        
    Returns:
        Filename with date prefix
    """
    if exif_date and len(exif_date) == 8 and exif_date.isdigit():
        return f"{exif_date}_{name}"
    return name


def find_and_replace(
    filenames: List[str],
    find: str,
    replace: str,
    use_regex: bool = False
) -> List[str]:
    """
    Find and replace in a list of filenames.
    
    Args:
        filenames: List of filenames
        find: String or pattern to find
        replace: Replacement string
        use_regex: Whether to use regex matching
        
    Returns:
        List of modified filenames
    """
    result = []
    for name in filenames:
        if use_regex:
            try:
                modified = re.sub(find, replace, name)
            except re.error:
                modified = name  # If regex is invalid, keep original
        else:
            modified = name.replace(find, replace)
        result.append(modified)
    
    return result

