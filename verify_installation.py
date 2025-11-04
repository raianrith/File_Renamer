#!/usr/bin/env python3
"""
Verification script to check if all dependencies are properly installed.
"""
import sys
import importlib

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    display_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name} is installed")
        return True
    except ImportError:
        print(f"❌ {display_name} is NOT installed")
        return False

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("✅ Python version is 3.10 or higher")
        return True
    else:
        print("❌ Python version should be 3.10 or higher")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Smart JPEG Renamer - Installation Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check Python version
    print("🐍 Checking Python version...")
    all_ok &= check_python_version()
    print()
    
    # Required packages
    print("📦 Checking required packages...")
    required = [
        ("streamlit", "streamlit"),
        ("google.generativeai", "google-generativeai"),
        ("PIL", "Pillow"),
        ("slugify", "python-slugify"),
        ("pandas", "pandas"),
        ("tenacity", "tenacity"),
        ("tqdm", "tqdm"),
    ]
    
    for module, package in required:
        all_ok &= check_import(module, package)
    
    print()
    
    # Optional packages
    print("🔧 Checking optional packages...")
    optional = [
        ("pytesseract", "pytesseract (OCR)"),
    ]
    
    for module, package in optional:
        if not check_import(module, package):
            print(f"   ⚠️  {package} is optional but recommended for OCR features")
    
    print()
    
    # Check Streamlit
    print("🌐 Checking Streamlit...")
    try:
        import streamlit
        version = streamlit.__version__
        print(f"✅ Streamlit version: {version}")
    except Exception as e:
        print(f"❌ Streamlit check failed: {e}")
        all_ok = False
    
    print()
    
    # Check API key
    print("🔑 Checking API key configuration...")
    import os
    
    if os.path.exists(".streamlit/secrets.toml"):
        print("✅ .streamlit/secrets.toml exists")
        
        # Try to read it
        try:
            with open(".streamlit/secrets.toml", "r") as f:
                content = f.read()
                if "GEMINI_API_KEY" in content and "your-gemini-api-key-here" not in content:
                    print("✅ GEMINI_API_KEY appears to be configured")
                else:
                    print("⚠️  GEMINI_API_KEY may need to be updated in secrets.toml")
        except Exception as e:
            print(f"⚠️  Could not read secrets.toml: {e}")
    else:
        print("⚠️  .streamlit/secrets.toml not found")
        print("   Create it from .streamlit/secrets.example.toml")
    
    # Check environment variable
    if os.environ.get("GEMINI_API_KEY"):
        print("✅ GEMINI_API_KEY found in environment variables")
    else:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
    
    print()
    
    # Summary
    print("=" * 60)
    if all_ok:
        print("✅ All required dependencies are installed!")
        print()
        print("🚀 You can now run the app with:")
        print("   streamlit run app.py")
    else:
        print("❌ Some dependencies are missing.")
        print()
        print("📝 To install missing dependencies:")
        print("   pip install -r requirements.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()

