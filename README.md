# Resume Tailoring Website Using LLM Technology

A web application that helps job seekers optimize their resumes for specific job postings using AI technology.

## Features

- Upload and parse resumes (DOCX and PDF formats)
- Extract key requirements from job listings (supports LinkedIn and generic job sites)
- Automatically tailor resume content to match job requirements
- Preview tailored resumes in HTML format
- Download professionally formatted DOCX files with native bullet points

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Integration**: OpenAI API (with support for multiple LLM providers)
- **Document Processing**: python-docx for DOCX generation, docx2txt for parsing
- **Web Scraping**: BeautifulSoup, Requests
- **Styling**: SCSS compilation with design token system

## Installation

1. Clone the repository:
   ```
   git clone <repository_url>
   cd manusResume6
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   SECRET_KEY=your_flask_secret_key
   OPENAI_API_KEY=your_openai_api_key
   # Optional: CLAUDE_API_KEY=your_claude_api_key
   # Optional: DOCX_USE_NATIVE_BULLETS=true
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at http://localhost:5000

## Project Structure

- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `claude_integration.py`: LLM API integration for resume tailoring (supports OpenAI and Claude)
- `job_parser.py`: Job listing parsing functionality
- `resume_formatter.py`: Resume formatting utilities
- `resume_processor.py`: Resume processing and analysis
- `utils/docx_builder.py`: Professional DOCX document generation with native bullet support
- `word_styles/`: Advanced DOCX styling system with native Word numbering
- `static/`: CSS, JavaScript, and uploads
  - `uploads/`: Location for uploaded resumes, job data, and tailored outputs.
  - `uploads/api_responses/`: Stores raw, timestamped LLM API responses for debugging.
  - `uploads/temp_session_data/`: Stores cleaned, tailored resume sections per user request (UUID-based filenames). **Requires cleanup.**
- `templates/`: HTML templates

## How It Works

1. Upload your resume (DOCX or PDF format)
2. Enter a job listing URL or paste job description
3. The application parses the job listing to extract requirements and skills
4. AI (OpenAI) tailors your resume to highlight relevant experience and skills
5. Preview your tailored resume in HTML format
6. Download your professionally formatted DOCX file

## Recent Updates

### ✅ Native DOCX Bullet Points (June 2025)
- Implemented production-ready native Word bullet system with 100% reliability
- Content-first architecture ensures proper style application
- Design token integration for consistent spacing across all formats
- Feature flag deployment with graceful degradation (`DOCX_USE_NATIVE_BULLETS=true`)
- Cross-platform compatibility (Word, LibreOffice, Google Docs)

### DOCX Generation Excellence
- Professional DOCX output with native Word formatting
- Table-based section headers for consistent visual appearance
- Advanced styling system using design tokens and SCSS
- Full-width role boxes matching section header styling
- Zero spacing inconsistencies through proper style hierarchy

### Resume Formatting Improvements
- Added professional YC-Eddie style formatting with consistent styling
- Native bullet points for optimal ATS compatibility
- Added horizontal line under contact information for cleaner visual separation
- Eliminated bold markdown formatting for cleaner document appearance
- Reduced line spacing between sections for more compact layout
- Perfect alignment between HTML preview and DOCX downloads

### LLM-Based Resume Parsing
- Implemented intelligent resume parsing using LLM (OpenAI/Claude)
- Added fallback to traditional parsing for resilience
- Improved section detection for varied resume formats
- Added caching to avoid repeated API calls

### LLM-Based Job Analysis
- Added comprehensive job analysis with AI insights
- Extraction of candidate profiles, hard/soft skills, and ideal candidate descriptions
- Enhanced UI with dedicated AI analysis section
- Primary support for OpenAI with Claude as secondary option

### Job Parser Enhancements
- Improved structure detection for job listings
- Enhanced parsing of "About the job" sections
- Better extraction of required skills and qualifications
- Support for more job posting formats

### AI API Integration
- Improved error handling for API requests (OpenAI primary, Claude secondary)
- Enhanced prompt engineering for better tailoring results
- Structured logging for API interactions

### User Interface
- Aligned Resume and Job Requirements panels side by side for better comparison
- Clean HTML preview with professional styling
- Single DOCX download button for optimal user experience

### Advanced DOCX Styling Architecture
- Design token system for centralized styling control
- SCSS compilation pipeline for consistent CSS generation
- Cross-format alignment between HTML preview and DOCX output
- Professional document generation with Microsoft Word native features

## DOCX Features Highlights

### Professional Document Generation
- **Native Word Bullets**: Production-ready bullet point system using Word's native numbering
- **Design Token Integration**: Centralized styling system ensures consistency
- **Cross-Platform Compatible**: Works perfectly in Word, LibreOffice, and Google Docs
- **ATS Optimized**: Native DOCX formatting for better applicant tracking system compatibility

### Advanced Styling System
- **Table-Based Headers**: Section headers use single-cell tables for perfect borders
- **Full-Width Role Boxes**: Job titles span the full content width like section headers
- **Content-First Architecture**: Ensures 100% reliable style application
- **Zero Spacing Issues**: Proper DOCX styling hierarchy eliminates formatting conflicts

### Technical Excellence
- **Feature Flag System**: Safe deployment with `DOCX_USE_NATIVE_BULLETS` environment variable
- **Idempotent Operations**: All document operations are safe to repeat
- **Comprehensive Logging**: Full traceability of style application and bullet creation
- **Error Recovery**: Graceful degradation if advanced features fail

## 🔒 Security & Privacy

This application handles sensitive personal information. **CRITICAL SECURITY MEASURES**:

### Before Making Repository Public
```bash
# Clean all user data (REQUIRED before public commits)
python scripts/cleanup_user_data.py --backup
```

### User Data Protection
- All uploaded resumes and personal data are automatically excluded from git
- Comprehensive `.gitignore` prevents accidental commits of sensitive files
- UUID-based session management for user privacy
- No permanent storage of personal information

### Deployment Security
- Use environment variables for API keys
- Enable HTTPS in production
- User data is automatically cleaned during deployment

**See [SECURITY.md](SECURITY.md) for complete security guidelines.**

## License

MIT

## Important Note: Temporary File Cleanup

The application currently stores temporary tailored resume data in `static/uploads/temp_session_data/` using unique request IDs. These files are necessary during the tailoring process but are not automatically cleaned up afterwards. **A cleanup mechanism (e.g., a scheduled task to delete files older than 24 hours) should be implemented** to prevent disk space issues in a production environment. 

For automated cleanup, use the provided script:
```bash
python scripts/cleanup_user_data.py --backup
``` 