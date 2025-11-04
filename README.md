# 📸 Smart JPEG Renamer

**Production-ready Streamlit app for intelligent batch renaming of JPEG files using Google Gemini Vision AI**

Automatically analyze image content and generate descriptive, consistent filenames with review capabilities, EXIF data support, optional OCR, and batch export.

---

## ✨ Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini Vision to understand image content
- 📝 **Smart Naming**: Generates descriptive filenames based on visual content
- 🔍 **Multiple Casing Styles**: kebab-case, snake_case, camelCase, or Title Case
- 📅 **EXIF Support**: Optional date prefixes from image metadata (YYYYMMDD_)
- 🔤 **OCR Integration**: Detect and include text from images (optional)
- ✏️ **Interactive Review**: Edit suggestions in an intuitive table interface
- 🔄 **Smart Caching**: Avoid redundant API calls with intelligent result caching
- 📦 **Batch Export**: Download renamed files as ZIP with CSV mapping
- 🛡️ **Error Handling**: Robust retry logic and fallback mechanisms
- 🎨 **Clean UI**: Modern, responsive interface with progress tracking

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Optional: Tesseract OCR for text detection

### Installation

1. **Clone or download this repository:**

```bash
git clone <your-repo-url>
cd File_Renamer
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up your API key:**

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

Or set environment variable:

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

4. **Run the app:**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### Basic Workflow

1. **Upload Images**: Click "Browse files" and select your JPEG files (up to 200 files, 50MB each)

2. **Configure Settings** (sidebar):
   - Choose AI model (gemini-1.5-flash recommended for speed)
   - Set max filename length (default: 60 characters)
   - Select casing style (kebab, snake, camel, or title)
   - Enable EXIF date prefix if desired
   - Enable OCR for text detection (requires Tesseract)
   - Adjust confidence threshold (0.0 - 1.0)

3. **Generate Suggestions**: Click "Generate Suggestions" to analyze images

4. **Review & Edit**: 
   - View proposed filenames in the interactive table
   - Edit any filename directly
   - Uncheck "Include" to skip files
   - Use batch actions to re-apply casing or dates
   - Use Find & Replace for bulk edits

5. **Export**:
   - Download ZIP of renamed files
   - Download CSV mapping (original → new names)
   - Save session log (JSON with full details)

### Advanced Features

#### Batch Actions

- **Re-apply Casing**: Update all filenames with current casing setting
- **Re-apply EXIF Dates**: Add/update date prefixes from EXIF data
- **Validate All**: Check for errors (duplicates, invalid characters, length)

#### Find & Replace

- Simple text replacement
- Regex support for advanced patterns
- Applies to all filenames in current batch

#### Caching

The app automatically caches AI results based on:
- Image content (SHA256 hash)
- Current settings (model, casing, length, etc.)

Re-running with same images and settings uses cached results (no API cost!).

---

## ⚙️ Configuration

### Model Selection

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gemini-2.5-flash | ⚡⚡⚡ | ⭐⭐⭐ | $ | Large batches, quick results (RECOMMENDED) |
| gemini-2.5-pro | ⚡⚡ | ⭐⭐⭐⭐ | $$ | High accuracy needed |
| gemini-2.0-flash | ⚡⚡⚡ | ⭐⭐ | $ | Alternative fast model |

**Recommendation**: Start with `gemini-2.5-flash` for best price/performance.

### Filename Rules

Generated filenames follow these rules:
- Only letters, numbers, hyphens, and underscores
- No spaces or special characters
- Maximum length enforced (default 60 chars)
- Automatic collision resolution with numeric suffixes (-1, -2, etc.)
- Original file extension preserved

### OCR Setup (Optional)

To enable OCR text detection:

1. Install Tesseract:
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

2. Enable "Include Detected Text (OCR)" in sidebar

3. Top frequent text tokens will be sent as context to the AI

---

## 🔒 Privacy & Security

### Data Handling

- ✅ Images processed **locally** in memory
- ✅ Only prompts and image data sent to Google Gemini API
- ✅ No server-side storage or persistence
- ✅ No analytics or tracking
- ⚠️ Image content **is sent to Google's API** for analysis

### API Costs

Google Gemini API usage incurs charges based on your plan:
- Free tier: Limited requests per minute
- Paid tier: Pay per 1K characters + image

**Cost Optimization Tips:**
- Use caching (automatic)
- Use gemini-1.5-flash for routine tasks
- Process in smaller batches to stay in free tier

---

## 🧪 Testing

Run the test suite:

```bash
# Test filename utilities
python tests/test_naming.py

# Test schema validation
python tests/test_schema.py

# Run all tests
python -m pytest tests/
```

### Manual QA Checklist

- [ ] Upload 1, 10, and 100 images
- [ ] Test with and without EXIF data
- [ ] Change casing/length settings and verify cache behavior
- [ ] Edit filenames in table and verify export
- [ ] Test Find & Replace (simple and regex)
- [ ] Verify ZIP contains correct renamed files
- [ ] Test with OCR enabled (if Tesseract installed)
- [ ] Check error handling (invalid API key, network issues)

---

## 📁 Project Structure

```
File_Renamer/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── secrets.example.toml       # API key template
├── src/
│   ├── __init__.py
│   ├── ai_client.py               # Gemini API client + retry logic
│   ├── exif_utils.py              # EXIF extraction and parsing
│   ├── ocr_utils.py               # Optional OCR functionality
│   ├── naming.py                  # Filename sanitization and casing
│   ├── caching.py                 # Result caching system
│   ├── ui.py                      # Streamlit UI components
│   └── zip_export.py              # Export utilities (ZIP, CSV, JSON)
└── tests/
    ├── __init__.py
    ├── test_naming.py             # Naming utility tests
    └── test_schema.py             # Schema validation tests
```

---

## 🛠️ Troubleshooting

### "Gemini API key not found"

- Check `.streamlit/secrets.toml` exists and contains `GEMINI_API_KEY`
- Or set environment variable: `export GEMINI_API_KEY="your-key"`

### "OCR requested but not available"

- Install Tesseract (see OCR Setup section)
- Verify installation: `tesseract --version`

### "Rate limit exceeded"

- Wait a few minutes (free tier has rate limits)
- Or upgrade to paid Gemini API plan
- Use caching to avoid repeat calls

### Slow processing

- Use `gemini-1.5-flash` instead of `gemini-1.5-pro`
- Process smaller batches
- Disable OCR if not needed

### Invalid filenames in output

- Click "Validate All" to check for errors
- Ensure max length is reasonable (60 recommended)
- Check for duplicate names (auto-fixed with suffixes)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional AI providers (OpenAI, Anthropic)
- More export formats (JSON metadata, XML)
- Batch processing for video files
- Custom naming templates
- Advanced EXIF filtering

---

## 📄 License

MIT License - feel free to use and modify for your projects.

---

## 🙏 Acknowledgments

- Google Gemini Vision API
- Streamlit framework
- Pillow (PIL) for image processing
- pytesseract for OCR

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Made with ❤️ for better file organization**

