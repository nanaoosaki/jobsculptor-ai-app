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
git clone https://github.com/nanaoosaki/manus_resume_site.git
cd manus_resume_site
```

**Note:** For private repositories, you'll need a GitHub Personal Access Token with 'repo' scope.

### 3. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install flask gunicorn python-dotenv openai python-docx requests beautifulsoup4
```

**Challenge:** PythonAnywhere free tier has a 512MB storage limit, which can be exceeded when installing all dependencies.
**Solution:** Install only essential packages and remove unnecessary files (like .git) to save space.

### 5. Create Web Application
- Go to the Web tab in PythonAnywhere dashboard
- Click "Add a new web app"
- Choose "Manual configuration" (not the Flask option)
- Select Python 3.9 or later

### 6. Configure Web App
- Source code directory: `/home/yourusername/manus_resume_site`
- Working directory: `/home/yourusername`
- Virtualenv: `/home/yourusername/manus_resume_site/venv`

**Challenge:** Mismatch between virtualenv Python version and web app Python version.
**Solution:** Ensure both are using the same Python version (modify web app to match virtualenv or recreate virtualenv).

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

### 9. Create Uploads Directory
```bash
mkdir -p ~/manus_resume_site/static/uploads
```

### 10. Security Settings
- Enable HTTPS (should be automatic)
- Password protection is optional (disabled by default)

### 11. Reload Web App
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

### 3. Import Errors
**Problem:** Application not importing correctly.
**Solution:**
- Check the error logs
- Ensure WSGI file has the correct path and import statement
- Verify that virtualenv is activated and has all dependencies

### 4. Missing Environment Variables
**Problem:** OpenAI API key and other environment variables not available.
**Solution:** Add them directly to the WSGI file as shown above.

### 5. Python Version Mismatch
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