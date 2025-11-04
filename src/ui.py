"""
Streamlit UI components and helpers.
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import pandas as pd
from PIL import Image
import io


def render_header():
    """Render the app header."""
    st.title("📸 Smart JPEG Renamer")
    st.markdown("""
    **Intelligent batch renaming powered by Google Gemini Vision**
    
    Upload your JPEG images, let AI analyze them, review suggestions, and download renamed files.
    [📖 View README](https://github.com/yourusername/smart-renamer)
    """)
    st.divider()


def render_settings_sidebar() -> Dict[str, Any]:
    """
    Render settings sidebar and return configuration.
    
    Returns:
        Dictionary of settings
    """
    st.sidebar.title("⚙️ Settings")
    
    # Model selection
    model = st.sidebar.selectbox(
        "Model",
        options=[
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ],
        index=0,
        help="Select the Gemini model to use (gemini-2.5-flash is fastest and cheapest)"
    )
    
    # Max filename length
    max_length = st.sidebar.slider(
        "Max Filename Length",
        min_value=20,
        max_value=100,
        value=60,
        help="Maximum length of generated filenames (excluding extension)"
    )
    
    # Casing style
    casing = st.sidebar.selectbox(
        "Filename Casing",
        options=["kebab", "snake", "camel", "title"],
        index=0,
        help="Choose the casing style for filenames"
    )
    
    # EXIF date prefix
    include_exif_date = st.sidebar.checkbox(
        "Include EXIF Date Prefix (YYYYMMDD_)",
        value=False,
        help="Prefix filenames with capture date from EXIF data"
    )
    
    # OCR
    include_ocr = st.sidebar.checkbox(
        "Include Detected Text (OCR)",
        value=False,
        help="Use OCR to detect text in images and include in context"
    )
    
    # Confidence threshold
    confidence_threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.1,
        help="Minimum confidence level for AI suggestions"
    )
    
    st.sidebar.divider()
    
    # Vertex AI toggle (advanced)
    use_vertex = st.sidebar.checkbox(
        "Use Vertex AI (Advanced)",
        value=False,
        help="Use Vertex AI instead of standard Gemini API"
    )
    
    if use_vertex:
        st.sidebar.warning("⚠️ Vertex AI requires GCP authentication")
        gcp_project = st.sidebar.text_input("GCP Project ID")
        gcp_region = st.sidebar.text_input("GCP Region", value="us-central1")
    else:
        gcp_project = None
        gcp_region = None
    
    return {
        'model': model,
        'max_length': max_length,
        'casing': casing,
        'include_exif_date': include_exif_date,
        'include_ocr': include_ocr,
        'confidence_threshold': confidence_threshold,
        'use_vertex': use_vertex,
        'gcp_project': gcp_project,
        'gcp_region': gcp_region
    }


def render_file_uploader(max_files: int = 200, max_size_mb: int = 50) -> List[Any]:
    """
    Render file uploader.
    
    Args:
        max_files: Maximum number of files
        max_size_mb: Maximum size per file in MB
        
    Returns:
        List of uploaded files
    """
    st.subheader("📁 Upload Images")
    
    uploaded_files = st.file_uploader(
        f"Choose JPEG files (max {max_files} files, {max_size_mb}MB each)",
        type=['jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Upload one or more JPEG images"
    )
    
    if uploaded_files:
        # Validate file count
        if len(uploaded_files) > max_files:
            st.error(f"⚠️ Too many files! Maximum is {max_files}. Only first {max_files} will be processed.")
            uploaded_files = uploaded_files[:max_files]
        
        # Validate file sizes
        max_size_bytes = max_size_mb * 1024 * 1024
        valid_files = []
        
        for file in uploaded_files:
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset
            
            if size <= max_size_bytes:
                valid_files.append(file)
            else:
                st.warning(f"⚠️ {file.name} exceeds {max_size_mb}MB and was skipped")
        
        st.success(f"✅ {len(valid_files)} files uploaded successfully")
        return valid_files
    
    return []


def render_preview_grid(files_data: List[Dict[str, Any]], cols: int = 4):
    """
    Render a grid of image thumbnails.
    
    Args:
        files_data: List of file dictionaries with 'bytes' and 'original_name'
        cols: Number of columns in grid
    """
    st.subheader("🖼️ Preview")
    
    if not files_data:
        st.info("No images to preview")
        return
    
    # Create grid
    rows = (len(files_data) + cols - 1) // cols
    
    for row in range(rows):
        columns = st.columns(cols)
        for col in range(cols):
            idx = row * cols + col
            if idx < len(files_data):
                with columns[col]:
                    file_info = files_data[idx]
                    
                    # Display thumbnail
                    try:
                        image = Image.open(io.BytesIO(file_info['bytes']))
                        st.image(image, use_container_width=True)
                        st.caption(file_info['original_name'])
                        
                        # Button to show details
                        if st.button(f"ℹ️", key=f"info_{idx}"):
                            st.session_state[f'show_modal_{idx}'] = True
                    except Exception as e:
                        st.error(f"Error: {e}")


def render_review_table(files_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Render an editable review table.
    
    Args:
        files_data: List of file dictionaries
        
    Returns:
        Updated DataFrame from the editor
    """
    st.subheader("✏️ Review & Edit")
    
    if not files_data:
        st.info("No files to review")
        return pd.DataFrame()
    
    # Create DataFrame
    df_data = []
    for i, file_info in enumerate(files_data):
        df_data.append({
            'Index': i,
            'Original': file_info['original_name'],
            'New Filename': file_info.get('new_name', ''),
            'Confidence': f"{file_info.get('confidence', 0):.2f}",
            'Tags': ', '.join(file_info.get('tags', [])),
            'Include': file_info.get('include', True)
        })
    
    df = pd.DataFrame(df_data)
    
    # Configure editor
    edited_df = st.data_editor(
        df,
        column_config={
            'Index': st.column_config.NumberColumn('ID', disabled=True),
            'Original': st.column_config.TextColumn('Original', disabled=True),
            'New Filename': st.column_config.TextColumn('New Filename', width='large'),
            'Confidence': st.column_config.TextColumn('Confidence', disabled=True),
            'Tags': st.column_config.TextColumn('Tags', disabled=True),
            'Include': st.column_config.CheckboxColumn('Include?', default=True)
        },
        hide_index=True,
        use_container_width=True,
        key='review_table'
    )
    
    return edited_df


def render_batch_actions():
    """Render batch action buttons."""
    st.subheader("🔧 Batch Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Re-apply Casing", use_container_width=True):
            st.session_state.reapply_casing = True
    
    with col2:
        if st.button("📅 Re-apply EXIF Dates", use_container_width=True):
            st.session_state.reapply_exif = True
    
    with col3:
        if st.button("✅ Validate All", use_container_width=True):
            st.session_state.validate_all = True


def render_find_replace():
    """Render find and replace widget."""
    with st.expander("🔍 Find & Replace"):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            find_text = st.text_input("Find", key='find_text')
        
        with col2:
            replace_text = st.text_input("Replace with", key='replace_text')
        
        with col3:
            st.write("")  # Spacing
            st.write("")  # Spacing
            use_regex = st.checkbox("Regex", key='use_regex')
        
        if st.button("Apply", use_container_width=True):
            if find_text:
                st.session_state.find_replace = {
                    'find': find_text,
                    'replace': replace_text,
                    'regex': use_regex
                }


def render_export_section():
    """Render export buttons."""
    st.subheader("📦 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("⬇️ Download ZIP", key='download_zip_btn', use_container_width=True)
    
    with col2:
        st.button("📄 Download CSV", key='download_csv_btn', use_container_width=True)
    
    with col3:
        st.button("📋 Save Session Log", key='download_log_btn', use_container_width=True)


def render_footer():
    """Render footer with privacy note."""
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p><strong>Privacy Note:</strong> Images are processed locally. Only prompts and image data 
        are sent to Google's Gemini API for analysis. No data is stored on our servers.</p>
        <p><strong>Billing:</strong> Usage of Gemini API may incur charges based on your Google Cloud billing.</p>
    </div>
    """, unsafe_allow_html=True)


def show_progress(current: int, total: int, message: str = "Processing"):
    """
    Show a progress bar.
    
    Args:
        current: Current progress
        total: Total items
        message: Progress message
    """
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{message}: {current}/{total}")

