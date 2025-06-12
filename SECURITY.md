# 🔒 Security Guide - Resume Tailor

## Critical User Data Protection

Resume Tailor handles sensitive personal information including resumes, contact details, work history, and educational background. This document outlines the security measures implemented to protect user privacy.

## 🚨 NEVER COMMIT USER DATA

This repository includes comprehensive `.gitignore` rules to prevent user data from being committed:

### Protected File Types
- **PDF/DOCX files**: `*.pdf`, `*.docx` (except templates)
- **LLM Analysis files**: `*_llm_parsed.json`, `*_llm_analysis.json`
- **Personal data files**: `*_contact.json`, `*_education.json`, etc.
- **Generated resumes**: `*tailored*.pdf`, `tailored_resume_*.pdf`
- **UUID-named files**: Session data and temporary files
- **Cache directories**: `job_analysis_cache/`, `api_responses/`, `temp_session_data/`

### Safe Files (Tracked in Git)
- `static/uploads/.gitkeep` - Preserves directory structure
- `*template*.docx` - Template files for the application
- `*sample*.docx` - Example files for documentation

## 🧹 Data Cleanup Tools

### Automated Cleanup Script
Use the provided script before making the repository public:

```bash
# Dry run - see what would be cleaned
python scripts/cleanup_user_data.py --dry-run

# Clean with backup
python scripts/cleanup_user_data.py --backup

# Clean without backup
python scripts/cleanup_user_data.py
```

### Manual Verification
After cleanup, verify the repository is clean:

```bash
# Check for any remaining user files
find . -name "*.pdf" -o -name "*.docx" | grep -v template
find static/uploads/ -type f | grep -v .gitkeep

# Check git status
git status --ignored
```

## 🚀 Deployment Security

### Production Environment Variables
Ensure these are set in production (Render, Heroku, etc.):

```bash
# Required
OPENAI_API_KEY=your_openai_key
FLASK_ENV=production
FLASK_DEBUG=False

# Optional security headers
FORCE_HTTPS=True
SESSION_COOKIE_SECURE=True
```

### File Upload Security
The application automatically:
- Generates unique UUIDs for uploaded files
- Validates file extensions (`.pdf`, `.docx` only)
- Limits file size to prevent abuse
- Creates temporary directories for processing

### Session Management
- User sessions are isolated by UUID
- Temporary files are cleaned up after processing
- No persistent storage of personal data between sessions

## 📁 Directory Structure - Safe vs. Sensitive

### ✅ Safe to Track in Git
```
static/
├── css/           # Stylesheets
├── js/            # JavaScript files  
├── styles/        # Additional styling
└── uploads/
    ├── .gitkeep   # Preserves directory
    └── template_resume.docx  # Template file
```

### 🔒 NEVER Track These
```
static/uploads/
├── *.pdf                    # User resumes
├── *.docx                   # Generated documents
├── *_llm_parsed.json       # Parsed personal data
├── *_llm_analysis.json     # LLM analysis results
├── job_analysis_cache/     # Cached job analyses
├── api_responses/          # API response cache
└── temp_session_data/      # Session temporary files
```

## 🛡️ Privacy by Design

### Data Minimization
- Only essential personal data is processed
- Temporary files are automatically cleaned
- No long-term storage of user information

### User Control
- Users can download their generated resumes
- No account creation required
- Session-based processing only

### Transparency
- Clear indication of what data is being processed
- Open source code for full transparency
- No hidden data collection

## 🚨 Incident Response

### If User Data is Accidentally Committed

1. **Immediate Actions**:
   ```bash
   # Remove from staging
   git reset HEAD~1
   
   # Clean working directory
   python scripts/cleanup_user_data.py
   
   # Force push to overwrite history (if already pushed)
   git push --force-with-lease
   ```

2. **For Public Repositories**:
   - Consider the repository compromised
   - Create a new repository from clean codebase
   - Update all deployment references
   - Notify affected users if identifiable

### Prevention Checklist
- [ ] Run cleanup script before public commits
- [ ] Verify `.gitignore` is working: `git status --ignored`
- [ ] Check for sensitive files: `git log --stat | grep -E "\.(pdf|docx)"`
- [ ] Use pre-commit hooks if working in a team

## 🔧 Development Best Practices

### Local Development
```bash
# Always clean before committing
python scripts/cleanup_user_data.py --dry-run
git add .
git status --ignored  # Should show no user files

# Use separate branch for testing with data
git checkout -b test-with-data
# ... test with real data ...
git checkout main
python scripts/cleanup_user_data.py
```

### CI/CD Pipeline
If using CI/CD, ensure:
- Environment variables are securely managed
- No user data directories are included in builds
- Deployment scripts use the cleanup tool

### Database Considerations
Currently using file-based storage. If migrating to a database:
- Implement proper data encryption
- Regular automated backups with encryption
- User data retention policies
- GDPR compliance if applicable

## 📞 Support

For security concerns or questions:
- Review this document
- Check `.gitignore` patterns
- Run the cleanup script
- Test with `--dry-run` first

Remember: **When in doubt, clean it out!** It's better to be overly cautious with user privacy. 