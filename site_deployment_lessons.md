# Deploying Resume Tailor on PythonAnywhere

This document outlines the steps to deploy the Resume Tailor application on PythonAnywhere, including challenges we encountered and their solutions.

## Overview of PythonAnywhere

PythonAnywhere is a platform that provides:
- Python execution environment in the cloud
- Web hosting for Python web applications
- Persistent file storage
- Free tier with limitations (512MB storage, 100 seconds CPU time daily)
- HTTPS certificates automatically

## Deployment Steps

### 1. Create a PythonAnywhere Account
- Sign up at pythonanywhere.com
- Free tier is sufficient for testing and demonstration

### 2. Clone the Repository
```bash
# Use a shallow clone to save disk space (free tier has 512MB limit)
git clone --depth=1 https://github.com/nanaoosaki/manus_resume_site.git
cd manus_resume_site
```

**Note:** For private repositories, you'll need a GitHub Personal Access Token with 'repo' scope.

### 3. Package Installation (No Virtual Environment)
For free tier accounts, it's recommended to skip virtual environments and use PythonAnywhere's system Python:

```bash
# Install only essential packages directly to your user account
pip install --user flask python-dotenv requests beautifulsoup4 python-docx werkzeug docx2txt flask-cors anthropic openai
```

### 4. Create Uploads Directory
```bash
mkdir -p ~/manus_resume_site/static/uploads
```

### 5. Create Web Application
- Go to the Web tab in PythonAnywhere dashboard
- Click "Add a new web app"
- Choose "Manual configuration" (not the Flask option)
- Select Python 3.9 or later

### 6. Configure Web App
- Source code directory: `/home/yourusername/manus_resume_site`
- Working directory: `/home/yourusername`
- **Important:** Delete any virtualenv setting (click the "×" button next to it) to use the system Python

### 7. Configure WSGI File
- The WSGI file is at `/var/www/yourusername_pythonanywhere_com_wsgi.py`
- Replace its contents with:

```python
import sys
import os

# Add environment variables
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"  # Replace with actual key
os.environ["SECRET_KEY"] = "your-secret-key"
os.environ["USE_LLM_RESUME_PARSING"] = "true"
os.environ["LLM_RESUME_PARSER_PROVIDER"] = "openai"
os.environ["USE_LLM_JOB_ANALYSIS"] = "true"
os.environ["LLM_JOB_ANALYZER_PROVIDER"] = "openai"

# Add your project directory to the Python path
path = '/home/yourusername/manus_resume_site'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import app as application
```

**Challenge:** Default WSGI file contains Hello World example code.
**Solution:** Replace it entirely with the configuration above.

### 8. Set Up Static Files
- In the Web tab, add a static files mapping:
  - URL: `/static/`
  - Directory: `/home/yourusername/manus_resume_site/static/`

### 9. Security Settings
- Enable HTTPS (should be automatic)
- Password protection is optional (disabled by default)

### 10. Reload Web App
- Click the green "Reload" button on the Web tab
- Check the Error log if the site doesn't work

## Troubleshooting Common Issues

### 1. Authentication Errors with Git
**Problem:** GitHub no longer accepts password authentication for git operations.
**Solution:** Use a Personal Access Token instead of your password.

### 2. Disk Quota Exceeded
**Problem:** The 512MB storage limit on the free tier can be easily exceeded.
**Solution:**
- Install only essential packages
- Remove .git directory to save space
- Delete unnecessary files
- Use `git clone --depth=1` for a shallow clone to save space
- Consider skipping virtual environments entirely (see below)

### 3. Virtual Environment Issues
**Problem:** Virtual environments consume significant disk space on the free tier and can lead to "Disk quota exceeded" errors.
**Solution:**
- **Skip virtual environments entirely** on the free tier and use PythonAnywhere's system Python
- Remove the virtualenv setting in the Web tab (click the "×" delete button next to the virtualenv path)
- Install packages with `pip install --user` which installs to your user directory
- Add all environment variables directly to the WSGI file

### 4. Alternative Virtual Environment Strategy for Free Tier
If you must use a virtual environment:
- Use `--without-pip` to create a minimal venv: `python -m venv venv --without-pip`
- Install only the absolute minimum packages needed
- Regularly clean up cache files: `find . -name "__pycache__" -type d -exec rm -rf {} +`
- Remove all development and test dependencies

### 5. Import Errors
**Problem:** Application not importing correctly.
**Solution:**
- Check the error logs
- Ensure WSGI file has the correct path and import statement
- Verify that virtualenv is activated and has all dependencies

### 6. Missing Environment Variables
**Problem:** OpenAI API key and other environment variables not available.
**Solution:** Add them directly to the WSGI file as shown above.

### 7. Python Version Mismatch
**Problem:** Virtualenv Python version doesn't match web app Python version.
**Solution:** Adjust web app Python version or recreate virtualenv with matching version.

## Custom Domain Setup

To use a custom domain (like jobsculptor.ai):
1. In the Web tab, add your domain
2. Configure DNS records at your domain registrar as instructed by PythonAnywhere
3. Wait for DNS propagation (24-48 hours)

## Performance Considerations

- Free tier has CPU time limitations (100 seconds/day)
- The application performance will degrade after CPU quota is used
- No cold starts unlike some serverless platforms (always on)
- Consider upgrading to paid tier ($5-7/month) for production use

## Security Considerations

- API keys are stored in the WSGI file, which is secure but not ideal
- Environment variables would be better but require a paid account
- HTTPS is enabled by default, protecting all communications 