# 🚀 Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies

```bash
# Using the setup script (recommended)
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure API Key

1. Get a Gemini API key from: https://makersuite.google.com/app/apikey

2. Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-actual-api-key-here"
```

Or set as environment variable:

```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

### Step 3: Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## First Run

1. **Upload Test Images**: Start with 3-5 JPEG files
2. **Default Settings**: Keep default settings for first try
3. **Generate**: Click "Generate Suggestions" button
4. **Review**: Check the proposed filenames
5. **Export**: Download ZIP or CSV

---

## Common Issues

### "No module named 'streamlit'"
→ Install dependencies: `pip install -r requirements.txt`

### "Gemini API key not found"
→ Create `.streamlit/secrets.toml` with your API key

### "OCR not available"
→ OCR is optional. Disable it in settings or install Tesseract:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from GitHub

---

## Example Workflow

```bash
# 1. Navigate to project
cd File_Renamer

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run app
streamlit run app.py

# 4. Open browser to http://localhost:8501

# 5. Upload JPEGs → Generate → Review → Export!
```

---

## Tips for Best Results

✅ **DO:**
- Use clear, well-lit photos
- Start with small batches (10-20 images)
- Review and edit suggestions
- Use caching (re-run = free!)

❌ **DON'T:**
- Upload 200 images on first try
- Use blurry or dark photos
- Expect perfect names every time (AI is smart but not perfect)
- Forget to review before export

---

## What's Next?

Check out the full [README.md](README.md) for:
- Advanced configuration
- All features explained
- Troubleshooting guide
- API cost optimization
- Testing instructions

---

**Questions?** Open an issue on GitHub or check the documentation.

