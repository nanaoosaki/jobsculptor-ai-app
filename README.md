# Resume Tailoring Website Using LLM Technology

A web application that helps job seekers optimize their resumes for specific job postings using Claude AI.

## Features

- Upload and parse resumes (DOCX format)
- Extract key requirements from job listings (supports LinkedIn and generic job sites)
- Automatically tailor resume content to match job requirements
- Preview and download tailored resumes

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Integration**: Claude API (Anthropic)
- **Document Processing**: python-docx
- **Web Scraping**: BeautifulSoup, Requests

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/nanaoosaki/manus_resume.git
   cd manus_resume
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   SECRET_KEY=your_flask_secret_key
   CLAUDE_API_KEY=your_claude_api_key
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at http://localhost:5000

## Project Structure

- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `claude_integration.py`: Claude API integration for resume tailoring
- `job_parser.py`: Job listing parsing functionality
- `resume_formatter.py`: Resume formatting utilities
- `resume_processor.py`: Resume processing and analysis
- `static/`: CSS, JavaScript, and uploads
  - `uploads/`: Location for uploaded resumes, job data, and tailored outputs.
  - `uploads/api_responses/`: Stores raw, timestamped LLM API responses for debugging.
  - `uploads/temp_session_data/`: Stores cleaned, tailored resume sections per user request (UUID-based filenames). **Requires cleanup.**
- `templates/`: HTML templates

## How It Works

1. Upload your resume (DOCX format)
2. Enter a job listing URL
3. The application parses the job listing to extract requirements and skills
4. Claude AI tailors your resume to highlight relevant experience and skills
5. Download your tailored resume

## Recent Updates

### Resume Formatting Improvements
- Added professional YC-Eddie style formatting with consistent styling
- Updated bullet points to use standard dot bullets for better readability
- Added horizontal line under contact information for cleaner visual separation
- Eliminated bold markdown formatting for cleaner document appearance
- Reduced line spacing between sections for more compact layout
- Consistent formatting between HTML preview and Word document downloads

### LLM-Based Resume Parsing
- Implemented intelligent resume parsing using LLM (Claude/OpenAI)
- Added fallback to traditional parsing for resilience
- Improved section detection for varied resume formats
- Added caching to avoid repeated API calls

### LLM-Based Job Analysis
- Added comprehensive job analysis with AI insights
- Extraction of candidate profiles, hard/soft skills, and ideal candidate descriptions
- Enhanced UI with dedicated AI analysis section
- Support for both Claude and OpenAI as analysis providers

### Job Parser Enhancements
- Improved structure detection for job listings
- Enhanced parsing of "About the job" sections
- Better extraction of required skills and qualifications
- Support for more job posting formats

### Claude API Integration
- Improved error handling for API requests
- Enhanced prompt engineering for better tailoring results
- Structured logging for API interactions

### User Interface
- Aligned Resume and Job Requirements panels side by side for better comparison
- Added HTTPS support using self-signed certificates

### PDF Formatting Enhancements (April 2025)
- Section headers now span full width for better visual consistency
- Professional summary content is properly left-aligned for improved readability
- Enhanced content filtering to prevent job analysis content from appearing in tailored output
- Professional summaries now follow a structured 3-part format (Recognition/Impact, Personal Attributes, Future Goals)
- Automatic conversion of bullet point summaries into cohesive paragraphs

### PDF Export Implementation
- Switched from Word document generation to PDF export for better consistency
- Implemented HTML-to-PDF conversion with professional styling
- Enhanced resume formatting with standard dot bullets and improved spacing

### Fixed PDF Formatting Issue
- Fixed PDF formatting issue that caused content to be incorrectly center-aligned in PDF outputs generated from PDF inputs
- Added PDF upload support, allowing users to upload and process PDF resume files
- Improved job parsing accuracy with enhanced LLM-based analysis
- Updated resume styling for better ATS compatibility

## License

MIT

## Important Note: Temporary File Cleanup

The application currently stores temporary tailored resume data in `static/uploads/temp_session_data/` using unique request IDs. These files are necessary during the tailoring process but are not automatically cleaned up afterwards. **A cleanup mechanism (e.g., a scheduled task to delete files older than 24 hours) should be implemented** to prevent disk space issues in a production environment. 