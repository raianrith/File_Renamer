"""
Caching utilities for storing and retrieving AI results.
"""
import hashlib
import json
from typing import Dict, Any, Optional
import streamlit as st


def compute_image_hash(image_bytes: bytes) -> str:
    """
    Compute SHA256 hash of image bytes.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Hex string of the hash
    """
    return hashlib.sha256(image_bytes).hexdigest()


def compute_settings_hash(settings: Dict[str, Any]) -> str:
    """
    Compute hash of settings dictionary.
    
    Args:
        settings: Dictionary of settings
        
    Returns:
        Hex string of the hash
    """
    # Sort keys for consistent hashing
    settings_str = json.dumps(settings, sort_keys=True)
    return hashlib.md5(settings_str.encode()).hexdigest()


def create_cache_key(image_hash: str, settings_hash: str) -> str:
    """
    Create a cache key from image and settings hashes.
    
    Args:
        image_hash: Hash of the image
        settings_hash: Hash of the settings
        
    Returns:
        Combined cache key
    """
    return f"{image_hash}_{settings_hash}"


@st.cache_data(ttl=3600)
def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached result.
    
    Args:
        cache_key: The cache key
        
    Returns:
        Cached result dictionary or None
    """
    # This function uses Streamlit's built-in caching
    # The actual storage happens in memory via st.cache_data
    return None


def cache_result(
    image_hash: str,
    settings: Dict[str, Any],
    result: Dict[str, Any]
) -> str:
    """
    Cache an AI result.
    
    Args:
        image_hash: Hash of the image
        settings: Settings dictionary
        result: Result to cache
        
    Returns:
        Cache key used
    """
    settings_hash = compute_settings_hash(settings)
    cache_key = create_cache_key(image_hash, settings_hash)
    
    # Store in session state for persistence during the session
    if 'result_cache' not in st.session_state:
        st.session_state.result_cache = {}
    
    st.session_state.result_cache[cache_key] = result
    return cache_key


def get_from_cache(
    image_hash: str,
    settings: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Retrieve result from cache.
    
    Args:
        image_hash: Hash of the image
        settings: Settings dictionary
        
    Returns:
        Cached result or None
    """
    settings_hash = compute_settings_hash(settings)
    cache_key = create_cache_key(image_hash, settings_hash)
    
    if 'result_cache' not in st.session_state:
        return None
    
    return st.session_state.result_cache.get(cache_key)


def clear_cache():
    """Clear all cached results."""
    if 'result_cache' in st.session_state:
        st.session_state.result_cache = {}
    
    # Also clear Streamlit's cache
    st.cache_data.clear()

