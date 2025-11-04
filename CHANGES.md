# Recent Changes

## UI Simplification & Cost Tracking (Latest)

### ✅ Changes Made:

1. **Removed Batch Actions**
   - Removed "Re-apply Casing" button
   - Removed "Re-apply EXIF Dates" button  
   - Removed "Validate All" button
   - Removed "Find & Replace" expander
   - Simplified UI for cleaner workflow

2. **Simplified Export Section**
   - Now shows only ONE "Download Renamed Images (ZIP)" button
   - Removed duplicate CSV and Session Log buttons
   - Made download button more prominent (primary style)
   - Full width button for better UX

3. **Added Cost Tracking**
   - Shows cost estimate BEFORE processing starts
   - Real-time cost tracking during generation
   - Displays:
     - Number of images
     - Model being used
     - Estimated cost in dollars
     - API credits/calls used
   - Final summary after completion

### 📊 Cost Estimates (Approximate):

| Model | Cost per Image | Cost for 10 Images | Cost for 100 Images |
|-------|----------------|-------------------|---------------------|
| gemini-2.5-flash | $0.0000075 | $0.000075 | $0.00075 |
| gemini-2.5-pro | $0.00025 | $0.0025 | $0.025 |
| gemini-2.0-flash | $0.0000075 | $0.000075 | $0.00075 |

**Note**: These are estimates. Actual costs may vary based on prompt complexity and Google's pricing.

### 🎨 New UI Flow:

```
1. Upload Images
   ↓
2. Click "Generate Suggestions"
   ↓
3. See Cost Estimate (before processing)
   ↓
4. Real-time Progress with Running Cost
   ↓
5. Review & Edit Filenames
   ↓
6. Download ZIP (single button)
```

### 🔧 Technical Changes:

**Files Modified:**
- `src/ui.py` - Removed batch actions, simplified export
- `app.py` - Added `estimate_cost()` function, removed batch handling, simplified export

**New Features:**
- Cost estimation based on model pricing
- Live cost tracking during processing
- Credit usage display
- Cleaner, more focused interface

---

## Previous Changes

### Model Name Updates
- Fixed model names from old `gemini-1.5-*` to new `gemini-2.5-*` and `gemini-2.0-*`
- Added support for latest Gemini 2.5 Flash (fastest, cheapest, recommended)

### Initial Release
- Full Smart JPEG Renamer with Gemini Vision AI
- EXIF support, OCR, multiple casing styles
- Comprehensive error handling and caching

