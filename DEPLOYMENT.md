# Deployment Guide for Streamlit Cloud

## 🚀 Deploy to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Gemini API key from https://makersuite.google.com/app/apikey

### Step 1: Push to GitHub

Make sure all files are committed and pushed:

```bash
git add .
git commit -m "Deploy Smart JPEG Renamer"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your repository: `raianrith/File_Renamer`
4. Main file path: `app.py`
5. Branch: `main`

### Step 3: Add Secrets

In Streamlit Cloud dashboard:

1. Click on your app
2. Go to **Settings** (⚙️)
3. Click **Secrets**
4. Add this content:

```toml
GEMINI_API_KEY = "your-actual-gemini-api-key-here"
```

5. Click **Save**

### Step 4: Reboot App

After adding secrets:
1. Click "Reboot app" in the Streamlit Cloud dashboard
2. Wait for deployment to complete
3. Your app is live! 🎉

---

## 📁 Required Files for Deployment

Make sure these files are in your GitHub repo:

- ✅ `app.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System packages (tesseract for OCR)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.example.toml` - Example secrets
- ✅ `src/` folder with all Python modules
- ✅ `README.md` - Documentation

---

## 🔧 Troubleshooting

### Import Errors

If you see `KeyError: 'src.ai_client'`:
1. Make sure the `src/` folder is in your GitHub repo
2. Check that `src/__init__.py` exists
3. Clear Streamlit Cloud cache: Settings → Clear cache → Reboot

### API Key Not Found

1. Double-check secrets in Streamlit Cloud dashboard
2. Make sure the key is named exactly `GEMINI_API_KEY`
3. No quotes around the key in the secrets UI
4. Reboot the app after adding secrets

### Module Not Found

1. Check `requirements.txt` has all dependencies
2. Push any missing dependencies to GitHub
3. Reboot the app in Streamlit Cloud

### Slow Performance

Streamlit Cloud has resource limits:
- Use `gemini-2.5-flash` (fastest, cheapest)
- Process smaller batches
- Large files may time out

---

## 📊 Monitoring

View logs in Streamlit Cloud:
1. Open your app dashboard
2. Click "Manage app"
3. View logs to see errors

---

## 🔄 Updating the App

To push updates:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Streamlit Cloud auto-deploys within 1-2 minutes!

---

## 🎯 Production Checklist

Before going live:

- [ ] API key added to Streamlit Cloud secrets
- [ ] All files pushed to GitHub
- [ ] Test with sample images
- [ ] Check logs for errors
- [ ] Verify ZIP download works
- [ ] Test "Start Over" button
- [ ] Confirm cost tracking displays correctly

---

## 🔗 Links

- **Streamlit Cloud**: https://share.streamlit.io/
- **GitHub Repo**: https://github.com/raianrith/File_Renamer
- **Gemini API**: https://makersuite.google.com/app/apikey
- **Documentation**: See README.md

---

**Your app URL will be:**
`https://raianrith-file-renamer-app-[random].streamlit.app`

