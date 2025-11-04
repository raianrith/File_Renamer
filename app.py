"""
Smart JPEG Renamer - Main Streamlit Application
"""
import streamlit as st
import os
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

# Import custom modules
from src.ui import (
    render_header,
    render_settings_sidebar,
    render_file_uploader,
    render_preview_grid,
    render_review_table,
    render_export_section,
    render_footer,
    show_progress
)
from src.ai_client import GeminiClient
from src.exif_utils import extract_exif, get_exif_date, format_exif_summary, create_thumbnail
from src.ocr_utils import is_ocr_available, extract_text_tokens, format_tokens_for_prompt
from src.naming import (
    sanitize_filename,
    apply_casing,
    ensure_uniqueness,
    validate_filename,
    add_exif_prefix,
    find_and_replace
)
from src.caching import compute_image_hash, get_from_cache, cache_result
from src.zip_export import (
    create_zip_with_renamed_files,
    create_csv_mapping,
    create_session_log,
    validate_files_for_export
)


# Page config
st.set_page_config(
    page_title="Weidert Internal AI JPEG File Renamer",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'files_data' not in st.session_state:
        st.session_state.files_data = []
    
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    
    if 'result_cache' not in st.session_state:
        st.session_state.result_cache = {}
    
    if 'reapply_casing' not in st.session_state:
        st.session_state.reapply_casing = False
    
    if 'reapply_exif' not in st.session_state:
        st.session_state.reapply_exif = False
    
    if 'validate_all' not in st.session_state:
        st.session_state.validate_all = False
    
    if 'find_replace' not in st.session_state:
        st.session_state.find_replace = None


def get_api_key() -> str:
    """
    Get Gemini API key from secrets or environment.
    
    Returns:
        API key string or empty string if not found
    """
    # Try Streamlit secrets first
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass
    
    # Fallback to environment variable
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return api_key


def process_uploaded_files(uploaded_files: List[Any]) -> List[Dict[str, Any]]:
    """
    Process uploaded files and prepare data structures.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        
    Returns:
        List of file data dictionaries
    """
    files_data = []
    
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        
        # Extract extension
        original_name = uploaded_file.name
        extension = os.path.splitext(original_name)[1]
        
        files_data.append({
            'original_name': original_name,
            'bytes': file_bytes,
            'extension': extension,
            'new_name': '',
            'confidence': 0.0,
            'tags': [],
            'reasons': '',
            'exif_date': None,
            'ocr_tokens': [],
            'latency': 0.0,
            'errors': [],
            'include': True
        })
    
    return files_data


def estimate_cost(num_images: int, model_name: str) -> Dict[str, Any]:
    """
    Estimate API cost for processing images.
    
    Args:
        num_images: Number of images to process
        model_name: Model name being used
        
    Returns:
        Dictionary with cost estimates
    """
    # Gemini API pricing (approximate)
    cost_per_image = {
        'gemini-2.5-flash': 0.0000075,  # $0.000075 per 10 images
        'gemini-2.5-pro': 0.00025,      # $0.0025 per 10 images
        'gemini-2.0-flash': 0.0000075,
        'gemini-flash-latest': 0.0000075,
        'gemini-pro-latest': 0.00025,
    }
    
    # Average processing time per image (seconds)
    time_per_image = {
        'gemini-2.5-flash': 2.5,      # ~2.5 seconds per image
        'gemini-2.5-pro': 4.0,        # ~4 seconds per image
        'gemini-2.0-flash': 2.5,
        'gemini-flash-latest': 2.5,
        'gemini-pro-latest': 4.0,
    }
    
    rate = cost_per_image.get(model_name, 0.00001)
    estimated_cost = num_images * rate
    
    avg_time = time_per_image.get(model_name, 3.0)
    estimated_time = num_images * avg_time
    
    return {
        'total_images': num_images,
        'cost_per_image': rate,
        'estimated_cost': estimated_cost,
        'credits_used': num_images,  # Simplified credit tracking
        'estimated_time': estimated_time,  # in seconds
        'time_per_image': avg_time
    }


def analyze_images(
    files_data: List[Dict[str, Any]],
    settings: Dict[str, Any],
    api_key: str
):
    """
    Analyze images using Gemini Vision API.
    
    Args:
        files_data: List of file data dictionaries
        settings: Settings dictionary
        api_key: Gemini API key
    """
    # Initialize AI client
    try:
        st.info(f"🔧 Initializing {settings['model']}...")
        client = GeminiClient(api_key, model_name=settings['model'])
        st.success(f"✅ AI client initialized successfully")
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini client: {e}")
        st.error("Please check your API key and model selection")
        return
    
    # Calculate and display cost estimate
    total_files = len(files_data)
    cost_info = estimate_cost(total_files, settings['model'])
    
    # Format estimated time
    est_time = cost_info['estimated_time']
    if est_time < 60:
        time_str = f"{est_time:.0f} seconds"
    else:
        minutes = int(est_time // 60)
        seconds = int(est_time % 60)
        time_str = f"{minutes}m {seconds}s"
    
    # Show cost estimate upfront
    st.info(f"""
    📊 **Processing Summary**
    - Images: {cost_info['total_images']}
    - Model: {settings['model']}
    - Estimated cost: ${cost_info['estimated_cost']:.6f}
    - Credits: ~{cost_info['credits_used']} API calls
    - Estimated time: ~{time_str}
    """)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    cost_text = st.empty()
    time_text = st.empty()
    
    import time
    start_time = time.time()
    
    for idx, file_info in enumerate(files_data):
        # Calculate elapsed and remaining time
        elapsed = time.time() - start_time
        if idx > 0:
            avg_time_per_image = elapsed / idx
            remaining_images = total_files - idx
            estimated_remaining = avg_time_per_image * remaining_images
            
            # Format times
            elapsed_str = f"{int(elapsed)}s"
            if elapsed >= 60:
                elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
            
            remaining_str = f"{int(estimated_remaining)}s"
            if estimated_remaining >= 60:
                remaining_str = f"{int(estimated_remaining // 60)}m {int(estimated_remaining % 60)}s"
            
            time_info = f"⏱️ Elapsed: {elapsed_str} | Remaining: ~{remaining_str}"
        else:
            time_info = f"⏱️ Starting..."
        
        # Update progress with cost tracking
        current_cost = (idx + 1) * cost_info['cost_per_image']
        status_text.text(f"Processing {idx + 1}/{total_files}: {file_info['original_name']}")
        cost_text.text(f"💰 Current cost: ${current_cost:.6f} | Credits used: {idx + 1}")
        time_text.text(time_info)
        
        try:
            # Extract EXIF data
            exif_data = extract_exif(file_info['bytes'])
            exif_date = get_exif_date(exif_data)
            file_info['exif_date'] = exif_date
            file_info['exif_data'] = exif_data
            
            # OCR if enabled
            ocr_tokens = []
            if settings['include_ocr'] and is_ocr_available():
                ocr_tokens = extract_text_tokens(file_info['bytes'])
                file_info['ocr_tokens'] = ocr_tokens
            
            # Check cache
            image_hash = compute_image_hash(file_info['bytes'])
            cached_result = get_from_cache(image_hash, settings)
            
            if cached_result:
                # Use cached result
                result = cached_result
                latency = 0.0
                status_text.text(f"✅ Using cached result for {file_info['original_name']}")
            else:
                # Call AI with error handling
                try:
                    status_text.text(f"🤖 Calling Gemini API for {file_info['original_name']}...")
                    ocr_tokens_str = format_tokens_for_prompt(ocr_tokens)
                    
                    result, latency = client.analyze_image(
                        file_info['bytes'],
                        casing=settings['casing'],
                        max_len=settings['max_length'],
                        ocr_tokens=ocr_tokens_str,
                        threshold=settings['confidence_threshold']
                    )
                    
                    status_text.text(f"✅ Got response in {latency:.1f}s")
                    
                    # Cache result
                    cache_result(image_hash, settings, result)
                except Exception as api_error:
                    error_msg = str(api_error)
                    st.error(f"⚠️ API Error for {file_info['original_name']}: {error_msg}")
                    
                    # Show more detailed error info
                    if "timeout" in error_msg.lower():
                        st.warning("API call timed out. The server might be overloaded. Try again in a moment.")
                    elif "404" in error_msg:
                        st.error("Model not found. Please check your model selection in settings.")
                    elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                        st.error("API key doesn't have permission. Check your Gemini API key settings.")
                    
                    # Use fallback
                    result = {
                        'proposed_filename': f'photo-{idx+1}',
                        'reasons': f'API error: {error_msg[:100]}',
                        'semantic_tags': ['photo'],
                        'confidence': 0.1
                    }
                    latency = 0.0
            
            # Process result
            proposed_name = result['proposed_filename']
            
            # Sanitize
            proposed_name = sanitize_filename(proposed_name, settings['max_length'])
            
            # Apply casing
            proposed_name = apply_casing(proposed_name, settings['casing'])
            
            # Add EXIF prefix if enabled
            if settings['include_exif_date'] and exif_date:
                proposed_name = add_exif_prefix(proposed_name, exif_date)
            
            # Update file info
            file_info['new_name'] = proposed_name + file_info['extension']
            file_info['confidence'] = result['confidence']
            file_info['tags'] = result['semantic_tags']
            file_info['reasons'] = result['reasons']
            file_info['latency'] = latency
            
        except Exception as e:
            file_info['errors'].append(str(e))
            file_info['new_name'] = f"error-{idx}{file_info['extension']}"
            st.warning(f"⚠️ Error processing {file_info['original_name']}: {e}")
        
        # Update progress
        progress_bar.progress((idx + 1) / total_files)
    
    # Ensure uniqueness
    new_names = [f['new_name'].rsplit('.', 1)[0] for f in files_data]
    extensions = [f['extension'] for f in files_data]
    unique_names = ensure_uniqueness(new_names, extensions)
    
    for idx, file_info in enumerate(files_data):
        file_info['new_name'] = unique_names[idx]
    
    # Calculate final stats
    total_time = time.time() - start_time
    final_cost = total_files * cost_info['cost_per_image']
    
    # Format final time
    if total_time < 60:
        total_time_str = f"{total_time:.1f} seconds"
    else:
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        total_time_str = f"{minutes}m {seconds}s"
    
    # Show final summary
    status_text.text("✅ Processing complete!")
    cost_text.success(f"💰 Total cost: ${final_cost:.6f} | Total credits: {total_files} API calls")
    time_text.success(f"⏱️ Completed in: {total_time_str} | Avg: {total_time/total_files:.1f}s per image")
    st.session_state.processing_complete = True


def apply_table_edits(edited_df: pd.DataFrame):
    """
    Apply edits from the review table to files_data.
    
    Args:
        edited_df: Edited DataFrame from st.data_editor
    """
    files_data = st.session_state.files_data
    
    for idx, row in edited_df.iterrows():
        file_idx = int(row['Index'])
        if file_idx < len(files_data):
            # Get the base name without extension
            new_name = row['New Filename']
            if '.' in new_name:
                base_name = new_name.rsplit('.', 1)[0]
                files_data[file_idx]['new_name'] = base_name + files_data[file_idx]['extension']
            else:
                files_data[file_idx]['new_name'] = new_name + files_data[file_idx]['extension']
            
            files_data[file_idx]['include'] = row['Include']


def handle_batch_actions(settings: Dict[str, Any]):
    """Handle batch action buttons."""
    files_data = st.session_state.files_data
    
    # Re-apply casing
    if st.session_state.reapply_casing:
        for file_info in files_data:
            base_name = file_info['new_name'].rsplit('.', 1)[0]
            # Remove EXIF prefix if present
            if '_' in base_name and base_name.split('_')[0].isdigit():
                prefix, rest = base_name.split('_', 1)
                rest = apply_casing(rest, settings['casing'])
                file_info['new_name'] = f"{prefix}_{rest}{file_info['extension']}"
            else:
                base_name = apply_casing(base_name, settings['casing'])
                file_info['new_name'] = base_name + file_info['extension']
        
        st.session_state.reapply_casing = False
        st.success("✅ Casing re-applied to all filenames")
    
    # Re-apply EXIF dates
    if st.session_state.reapply_exif:
        for file_info in files_data:
            if settings['include_exif_date'] and file_info.get('exif_date'):
                base_name = file_info['new_name'].rsplit('.', 1)[0]
                # Remove existing prefix if present
                if '_' in base_name and base_name.split('_')[0].isdigit():
                    base_name = base_name.split('_', 1)[1]
                
                base_name = add_exif_prefix(base_name, file_info['exif_date'])
                file_info['new_name'] = base_name + file_info['extension']
        
        st.session_state.reapply_exif = False
        st.success("✅ EXIF dates re-applied to all filenames")
    
    # Validate all
    if st.session_state.validate_all:
        errors = []
        for file_info in files_data:
            base_name = file_info['new_name'].rsplit('.', 1)[0]
            is_valid, error_msg = validate_filename(base_name, settings['max_length'])
            if not is_valid:
                errors.append(f"{file_info['original_name']}: {error_msg}")
        
        if errors:
            st.error("❌ Validation errors:\n" + "\n".join(errors))
        else:
            st.success("✅ All filenames are valid!")
        
        st.session_state.validate_all = False
    
    # Find and replace
    if st.session_state.find_replace:
        fr = st.session_state.find_replace
        new_names = [f['new_name'].rsplit('.', 1)[0] for f in files_data]
        modified_names = find_and_replace(
            new_names,
            fr['find'],
            fr['replace'],
            fr['regex']
        )
        
        for idx, file_info in enumerate(files_data):
            file_info['new_name'] = modified_names[idx] + file_info['extension']
        
        st.session_state.find_replace = None
        st.success(f"✅ Replaced '{fr['find']}' with '{fr['replace']}'")


def main():
    """Main application logic."""
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render settings sidebar
    settings = render_settings_sidebar()
    
    # Check API key
    api_key = get_api_key()
    
    if not api_key:
        st.warning("⚠️ Gemini API key not found!")
        st.info("""
        Please set your API key in one of these ways:
        1. Create `.streamlit/secrets.toml` and add: `GEMINI_API_KEY = "your-key"`
        2. Set environment variable: `export GEMINI_API_KEY="your-key"`
        """)
        st.stop()
    
    # Check OCR availability
    if settings['include_ocr'] and not is_ocr_available():
        st.sidebar.warning("⚠️ OCR requested but pytesseract not available. OCR will be disabled.")
        settings['include_ocr'] = False
    
    # File uploader
    uploaded_files = render_file_uploader()
    
    # Process uploaded files
    if uploaded_files:
        # Check if these are new files (different count or different names)
        current_names = [f.name for f in uploaded_files]
        existing_names = [f['original_name'] for f in st.session_state.files_data] if st.session_state.files_data else []
        
        if current_names != existing_names:
            st.session_state.files_data = process_uploaded_files(uploaded_files)
            st.session_state.processing_complete = False
    elif not uploaded_files:
        # No files uploaded, clear state if needed
        if st.session_state.files_data:
            st.session_state.files_data = []
            st.session_state.processing_complete = False
    
    # Preview grid
    if st.session_state.files_data:
        render_preview_grid(st.session_state.files_data)
        
        st.divider()
        
        # Generate suggestions button
        if not st.session_state.processing_complete:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Generate Suggestions", use_container_width=True, type="primary"):
                    analyze_images(st.session_state.files_data, settings, api_key)
        
        # Review table (if processing complete)
        if st.session_state.processing_complete:
            st.divider()
            
            # Review table
            edited_df = render_review_table(st.session_state.files_data)
            
            # Apply table edits
            if edited_df is not None and not edited_df.empty:
                apply_table_edits(edited_df)
            
            st.divider()
            
            # Export section - simplified to just ZIP download
            render_export_section()
            
            # Validate before export
            is_valid, errors = validate_files_for_export(st.session_state.files_data)
            
            if is_valid:
                # Create ZIP
                try:
                    zip_bytes = create_zip_with_renamed_files(st.session_state.files_data)
                    st.download_button(
                        label="⬇️ Download Renamed Images (ZIP)",
                        data=zip_bytes,
                        file_name=f"renamed_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error creating ZIP: {e}")
            else:
                st.error("❌ Cannot export: " + "; ".join(errors))
            
            # Reset button
            st.divider()
            if st.button("🔄 Start Over", use_container_width=False):
                # Clear all session state
                st.session_state.files_data = []
                st.session_state.processing_complete = False
                # Clear any cached data
                if 'result_cache' in st.session_state:
                    st.session_state.result_cache = {}
                # Increment uploader key to reset file uploader widget
                if 'uploader_key' in st.session_state:
                    st.session_state.uploader_key += 1
                st.rerun()
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()

