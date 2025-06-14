# Render Deployment Guide for Resume Tailor

## 📋 Pre-Deployment Checklist

✅ **Files Created for Deployment:**
- `Procfile` - Tells Render how to start the app
- `render.yaml` - Render configuration with system dependencies
- `startup.py` - Production environment setup script
- `validate_deployment.py` - Deployment validation script
- Updated `app.py` - Dynamic port configuration and health check
- Updated `requirements.txt` - Production dependencies with WeasyPrint and Playwright
- `.gitkeep` files - Ensure required directories exist in deployment

## 🚀 Deployment Steps

### 1. Validate Deployment Locally (Optional but Recommended)
```bash
python validate_deployment.py
```
This will check that all dependencies and configurations are correct.

### 2. Connect to GitHub (if not already done)
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Create Render Service
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select `jobsculptor-ai-app` repository
4. Choose `main` branch

### 4. Configure Deployment Settings

**Basic Settings:**
- **Name:** `manus-resume-tailor` (or your preference)
- **Environment:** `Python`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

**Advanced Settings:**
- **Python Version:** `3.12.10`
- **Plan:** Free (or paid for better performance)

### 5. Set Environment Variables

**Required Variables:**
```
FLASK_SECRET_KEY = [Auto-generated by Render]
CLAUDE_API_KEY = [Your Claude API key]
OPENAI_API_KEY = [Your OpenAI API key]
FLASK_ENV = production
USE_LLM_RESUME_PARSING = true
LLM_RESUME_PARSER_PROVIDER = auto
USE_LLM_JOB_ANALYSIS = true
LLM_JOB_ANALYZER_PROVIDER = auto
USE_ENHANCED_SPACING = true
```

**How to Add Environment Variables:**
1. In Render dashboard → Your service → Environment
2. Add each variable above
3. For API keys, mark as "Secret" 🔒

### 6. System Dependencies (Handled Automatically)

The `render.yaml` file includes:
- WeasyPrint dependencies (Cairo, Pango, etc.)
- PDF generation libraries
- System packages for Linux deployment

### 7. Deploy!

Click **"Create Web Service"** and wait for deployment to complete.

## 🔧 Troubleshooting

### Common Issues:

**1. WeasyPrint Build Failures:**
- Render installs system dependencies automatically via `render.yaml`
- If issues persist, check build logs for missing packages

**2. API Key Issues:**
- Ensure `CLAUDE_API_KEY` and `OPENAI_API_KEY` are set
- App runs in demo mode without API keys (limited functionality)

**3. Static Files Not Loading:**
- Flask serves static files automatically
- Check `static/` directory is included in repository

**4. Port Issues:**
- App now uses `PORT` environment variable (set by Render)
- Falls back to 5000 for local development

### Debug Mode:
- Production: `FLASK_ENV=production` (debug=False)
- Development: `FLASK_ENV=development` (debug=True)

## 📊 Expected Functionality

**✅ Working Features:**
- Resume upload and parsing
- Job description analysis
- AI-powered resume tailoring
- PDF generation
- DOCX file handling
- All testing frameworks and APIs

**⚠️ Limitations on Free Tier:**
- 512MB RAM (may limit concurrent users)
- Services sleep after 15 minutes of inactivity
- Consider upgrading for production use

## 🔗 Post-Deployment

1. **Test the deployed app:** `https://your-app-name.onrender.com`
2. **Health check:** `https://your-app-name.onrender.com/health`
3. **Monitor logs:** Render Dashboard → Your Service → Logs
4. **Update environment variables:** Dashboard → Environment tab

### 🧪 Test Core Functionality

**Basic Tests:**
- ✅ Home page loads
- ✅ Health check returns green status
- ✅ Resume upload works
- ✅ Job analysis works (if API keys configured)
- ✅ PDF generation works
- ✅ DOCX generation works

**Performance Notes:**
- First request may be slow (cold start)
- PDF generation uses WeasyPrint (requires system dependencies)
- Large file uploads may timeout on free tier

## 📋 File Structure Summary

```
├── app.py                    # Main Flask application
├── Procfile                  # Render startup command
├── render.yaml              # Render configuration
├── requirements.txt         # Python dependencies
├── config.py                # Configuration management
├── static/                  # Static files (CSS, JS, uploads)
├── templates/               # HTML templates
├── utils/                   # Utility modules
├── word_styles/             # DOCX styling modules
└── *_handler.py            # Route handlers
```

## 🎯 Next Steps

1. Deploy to Render using the steps above
2. Test all functionality
3. Add your API keys for full AI features
4. Monitor performance and upgrade plan if needed

Your resume tailor is ready for production! 🚀 