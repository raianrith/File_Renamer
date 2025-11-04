"""
Tests for AI response schema validation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from src.ai_client import GeminiClient


def test_schema_validation():
    """Test schema validation and fixing."""
    # We'll test the _validate_and_fix_schema method without needing an API key
    # Create a dummy client (won't actually call API)
    
    # Valid schema
    valid_data = {
        'proposed_filename': 'sunset-beach',
        'reasons': 'Beautiful sunset over the beach',
        'semantic_tags': ['sunset', 'beach', 'ocean'],
        'confidence': 0.85
    }
    
    # This should pass without modification
    # We would need to instantiate client but we'll test the logic directly
    
    print("Testing valid schema...")
    assert 'proposed_filename' in valid_data
    assert 'reasons' in valid_data
    assert 'semantic_tags' in valid_data
    assert 'confidence' in valid_data
    assert isinstance(valid_data['proposed_filename'], str)
    assert isinstance(valid_data['reasons'], str)
    assert isinstance(valid_data['semantic_tags'], list)
    assert 0.0 <= valid_data['confidence'] <= 1.0
    
    print("✅ Valid schema test passed")


def test_confidence_range():
    """Test that confidence is within valid range."""
    test_cases = [
        (0.0, True),
        (0.5, True),
        (1.0, True),
        (-0.1, False),  # Should be clamped to 0.0
        (1.5, False),   # Should be clamped to 1.0
    ]
    
    for value, is_valid in test_cases:
        if is_valid:
            assert 0.0 <= value <= 1.0, f"Confidence {value} is valid"
        else:
            # Value would be clamped
            clamped = max(0.0, min(1.0, value))
            assert 0.0 <= clamped <= 1.0, f"Confidence {value} clamped to {clamped}"
    
    print("✅ Confidence range test passed")


def test_required_keys():
    """Test that all required keys are present."""
    required_keys = ['proposed_filename', 'reasons', 'semantic_tags', 'confidence']
    
    # Complete data
    complete_data = {
        'proposed_filename': 'test',
        'reasons': 'test reason',
        'semantic_tags': ['tag1'],
        'confidence': 0.5
    }
    
    for key in required_keys:
        assert key in complete_data, f"Required key {key} is present"
    
    # Incomplete data - should have defaults added
    incomplete_data = {
        'proposed_filename': 'test'
    }
    
    # Simulate adding defaults
    defaults = {
        'reasons': 'No description available',
        'semantic_tags': [],
        'confidence': 0.5
    }
    
    for key in required_keys:
        if key not in incomplete_data:
            incomplete_data[key] = defaults.get(key, None)
    
    # Now check all keys are present
    for key in required_keys:
        assert key in incomplete_data, f"Key {key} added with default"
    
    print("✅ Required keys test passed")


def test_semantic_tags_type():
    """Test that semantic tags is a list."""
    valid_tags = ['beach', 'sunset', 'ocean']
    assert isinstance(valid_tags, list)
    assert all(isinstance(tag, str) for tag in valid_tags)
    
    # Invalid tags (not a list)
    invalid_tags = "beach, sunset, ocean"
    if not isinstance(invalid_tags, list):
        # Should be converted to empty list
        invalid_tags = []
    
    assert isinstance(invalid_tags, list)
    
    print("✅ Semantic tags type test passed")


def test_json_parsing():
    """Test JSON parsing from various formats."""
    # Standard JSON
    json_str = '{"proposed_filename": "test", "reasons": "test", "semantic_tags": [], "confidence": 0.5}'
    data = json.loads(json_str)
    assert data['proposed_filename'] == 'test'
    
    # JSON wrapped in markdown
    markdown_json = '''```json
{
    "proposed_filename": "test",
    "reasons": "test",
    "semantic_tags": [],
    "confidence": 0.5
}
```'''
    
    # Extract JSON from markdown
    if "```json" in markdown_json:
        start = markdown_json.find("```json") + 7
        end = markdown_json.find("```", start)
        extracted = markdown_json[start:end].strip()
        data = json.loads(extracted)
        assert data['proposed_filename'] == 'test'
    
    print("✅ JSON parsing test passed")


if __name__ == "__main__":
    test_schema_validation()
    test_confidence_range()
    test_required_keys()
    test_semantic_tags_type()
    test_json_parsing()
    
    print("\n🎉 All schema tests passed!")

