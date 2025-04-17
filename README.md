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

## License

MIT 