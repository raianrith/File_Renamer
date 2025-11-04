"""
Tests for filename sanitization and naming utilities.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.naming import (
    sanitize_filename,
    apply_casing,
    ensure_uniqueness,
    validate_filename,
    add_exif_prefix,
    find_and_replace
)


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test basic sanitization
    assert sanitize_filename("Hello World") == "hello_world"
    assert sanitize_filename("Test@#$%File") == "test_file"
    
    # Test length truncation
    long_name = "a" * 100
    result = sanitize_filename(long_name, max_length=60)
    assert len(result) <= 60
    
    # Test empty input
    assert sanitize_filename("") == "unnamed"
    
    # Test special characters
    assert sanitize_filename("café-résumé") == "cafe_resume"
    
    print("✅ test_sanitize_filename passed")


def test_apply_casing():
    """Test casing conversions."""
    test_name = "hello_world_test"
    
    # Kebab case
    assert apply_casing(test_name, "kebab") == "hello-world-test"
    
    # Snake case
    assert apply_casing(test_name, "snake") == "hello_world_test"
    
    # Camel case
    assert apply_casing(test_name, "camel") == "helloWorldTest"
    
    # Title case
    assert apply_casing(test_name, "title") == "Hello World Test"
    
    print("✅ test_apply_casing passed")


def test_ensure_uniqueness():
    """Test uniqueness enforcement."""
    # Test with duplicates
    filenames = ["photo", "photo", "photo", "image"]
    extensions = [".jpg", ".jpg", ".jpg", ".jpg"]
    
    result = ensure_uniqueness(filenames, extensions)
    
    # Check all are unique
    assert len(result) == len(set([r.lower() for r in result]))
    
    # Check original is preserved
    assert "photo.jpg" in result
    
    # Check suffixes added
    assert any("-1" in r for r in result)
    
    print("✅ test_ensure_uniqueness passed")


def test_validate_filename():
    """Test filename validation."""
    # Valid names
    is_valid, msg = validate_filename("hello-world")
    assert is_valid
    
    is_valid, msg = validate_filename("test_file_123")
    assert is_valid
    
    # Invalid: empty
    is_valid, msg = validate_filename("")
    assert not is_valid
    
    # Invalid: too long
    is_valid, msg = validate_filename("a" * 100, max_length=60)
    assert not is_valid
    
    # Invalid: illegal characters
    is_valid, msg = validate_filename("hello/world")
    assert not is_valid
    
    is_valid, msg = validate_filename("test:file")
    assert not is_valid
    
    print("✅ test_validate_filename passed")


def test_add_exif_prefix():
    """Test EXIF date prefix."""
    # Valid date
    result = add_exif_prefix("photo", "20231115")
    assert result == "20231115_photo"
    
    # Invalid date (not 8 digits)
    result = add_exif_prefix("photo", "2023")
    assert result == "photo"
    
    # Invalid date (non-numeric)
    result = add_exif_prefix("photo", "abcdefgh")
    assert result == "photo"
    
    # Empty date
    result = add_exif_prefix("photo", "")
    assert result == "photo"
    
    print("✅ test_add_exif_prefix passed")


def test_find_and_replace():
    """Test find and replace."""
    filenames = ["hello-world", "goodbye-world", "test-file"]
    
    # Simple replace
    result = find_and_replace(filenames, "world", "universe", use_regex=False)
    assert "hello-universe" in result
    assert "goodbye-universe" in result
    
    # Regex replace
    result = find_and_replace(filenames, r"-\w+$", "-replaced", use_regex=True)
    assert all("replaced" in r for r in result)
    
    print("✅ test_find_and_replace passed")


if __name__ == "__main__":
    test_sanitize_filename()
    test_apply_casing()
    test_ensure_uniqueness()
    test_validate_filename()
    test_add_exif_prefix()
    test_find_and_replace()
    
    print("\n🎉 All naming tests passed!")

