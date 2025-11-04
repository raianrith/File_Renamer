"""
ZIP file creation and CSV export utilities.
"""
import zipfile
import io
from typing import List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime
from PIL import Image


def create_zip_with_renamed_files(
    files_data: List[Dict[str, Any]]
) -> bytes:
    """
    Create a ZIP file containing renamed image files in their output formats.
    
    Args:
        files_data: List of dictionaries with keys:
            - 'original_name': original filename
            - 'new_name': new filename
            - 'pil_image': PIL Image object
            - 'output_format': target format (jpg, png, etc.)
            - 'include': whether to include this file
            
    Returns:
        ZIP file as bytes
    """
    from src.format_converter import FormatConverter
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_info in files_data:
            if file_info.get('include', True):
                new_name = file_info['new_name']
                
                # Convert PIL image to the appropriate output format
                if 'pil_image' in file_info and 'output_format' in file_info:
                    pil_image = file_info['pil_image']
                    output_format = file_info['output_format'].upper()
                    file_bytes = FormatConverter.convert_pil_to_bytes(pil_image, output_format)
                else:
                    # Fallback to original bytes if no PIL image available
                    file_bytes = file_info['bytes']
                
                # Add file to ZIP
                zip_file.writestr(new_name, file_bytes)
    
    return zip_buffer.getvalue()


def create_csv_mapping(
    files_data: List[Dict[str, Any]]
) -> str:
    """
    Create CSV mapping of original to new filenames.
    
    Args:
        files_data: List of dictionaries with file information
            
    Returns:
        CSV string
    """
    rows = []
    
    for file_info in files_data:
        if file_info.get('include', True):
            rows.append({
                'Original Filename': file_info['original_name'],
                'New Filename': file_info['new_name'],
                'Confidence': file_info.get('confidence', 'N/A'),
                'Tags': ', '.join(file_info.get('tags', [])),
                'Reasons': file_info.get('reasons', '')
            })
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def create_session_log(
    files_data: List[Dict[str, Any]],
    settings: Dict[str, Any]
) -> str:
    """
    Create a detailed session log in JSON format.
    
    Args:
        files_data: List of dictionaries with file information
        settings: Settings used for processing
            
    Returns:
        JSON string
    """
    import json
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'settings': settings,
        'files': []
    }
    
    for file_info in files_data:
        file_log = {
            'original_name': file_info['original_name'],
            'new_name': file_info['new_name'],
            'included': file_info.get('include', True),
            'confidence': file_info.get('confidence', None),
            'semantic_tags': file_info.get('tags', []),
            'reasons': file_info.get('reasons', ''),
            'exif_date': file_info.get('exif_date', None),
            'ocr_tokens': file_info.get('ocr_tokens', []),
            'api_latency': file_info.get('latency', None),
            'errors': file_info.get('errors', [])
        }
        log_data['files'].append(file_log)
    
    return json.dumps(log_data, indent=2)


def validate_files_for_export(
    files_data: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """
    Validate files before export.
    
    Args:
        files_data: List of dictionaries with file information
            
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    included_files = [f for f in files_data if f.get('include', True)]
    
    if not included_files:
        errors.append("No files selected for export")
        return False, errors
    
    # Check for duplicate filenames
    new_names = [f['new_name'] for f in included_files]
    seen = set()
    duplicates = set()
    
    for name in new_names:
        if name.lower() in seen:
            duplicates.add(name)
        seen.add(name.lower())
    
    if duplicates:
        errors.append(f"Duplicate filenames found: {', '.join(duplicates)}")
    
    # Check for empty filenames
    empty_names = [f['original_name'] for f in included_files if not f['new_name'].strip()]
    if empty_names:
        errors.append(f"Empty filenames for: {', '.join(empty_names)}")
    
    return len(errors) == 0, errors

