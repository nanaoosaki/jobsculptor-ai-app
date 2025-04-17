# Resume Tailoring Website Using LLM Technology

## Project Overview
This application helps users tailor their resumes to match specific job listings using Claude AI. The application analyzes job postings, extracts requirements, and optimizes the resume accordingly.

## Files and Structure
- **app.py**: Main Flask application entrypoint
- **config.py**: Configuration settings (API keys, upload paths)
- **upload_handler.py**: Handles resume file uploads
- **resume_processor.py**: Processes and analyzes uploaded resumes
- **resume_formatter.py**: Formats resumes into a standardized structure
- **job_parser.py**: Parses job listings from URLs (LinkedIn and generic)
- **claude_integration.py**: Interfaces with Claude AI for resume tailoring
- **llm_resume_parser.py**: LLM-based resume parsing with fallback mechanism
- **tailoring_handler.py**: Orchestrates the tailoring process
- **format_handler.py**: API routes for resume formatting
- **job_parser_handler.py**: API routes for job parsing
- **static/css/styles.css**: Styling for the application
- **static/js/main.js**: Frontend JavaScript
- **templates/index.html**: Main HTML interface
- **static/uploads/**: Stores uploaded and processed files

## Input/Output Flow
1. **Input**: User uploads DOCX resume and provides job listing URL
2. **Resume Processing**:
   - Resume is uploaded and saved to uploads directory
   - LLM parser extracts sections (contact, summary, experience, education, skills, etc.)
   - If LLM parsing fails, traditional heading-based parsing is used as fallback
   - Parsed sections are displayed in UI and stored for tailoring
3. **Job Listing Processing**:
   - Job URL is processed to extract content based on site type
   - Requirements and skills are extracted from job description
   - Full job listing sections are displayed in UI
4. **Tailoring**:
   - LLM (Claude/OpenAI) analyzes resume sections against job requirements
   - Each section is tailored individually with specific prompts
   - Tailored content is assembled into a new document
5. **Output**: 
   - Tailored resume available for download as DOCX
   - HTML preview of tailored content displayed in UI

## Fixes Applied
1. Added proper secret key for Flask app security
2. Created correct folder structure for Flask app (templates/, static/)
3. Fixed template_resume.docx path issue by copying to static/uploads directory
4. Fixed 'summary' KeyError by properly initializing empty sections
5. Enhanced section handling to properly check for empty content before processing
6. Fixed regex character range error in job_parser.py that was causing LinkedIn job parsing to fail
7. Fixed demo mode vs. API mode by ensuring the Claude API key is properly configured
8. Added .env and sensitive files to .gitignore to prevent exposing API keys
9. Improved UI layout by aligning "User Resume Parsed" and "Job Requirements" panels side by side
10. Made HTTP/HTTPS dynamic based on certificate availability
11. Ensured proper dependency installation for PDF and DOCX processing
12. Significantly improved job parsing to capture "About the job" and all relevant sections
13. Enhanced section detection in job listings using advanced pattern matching
14. Fixed Claude API integration to properly use official Anthropic SDK
15. Removed demo mode fallback to ensure consistent API usage and testing
16. Implemented LLM-based resume parsing with traditional parsing fallback
17. Fixed upload handler to use LLM parsing during initial resume upload
18. Added configuration settings for LLM provider selection and enabling/disabling

## LLM Resume Parsing Implementation
- Created new `llm_resume_parser.py` module for LLM-based resume parsing
- Integrated both Claude and OpenAI as parsing options
- Implemented auto-detection of available API keys
- Added robust validation, error handling, and logging
- Created JSON caching system to avoid repeated API calls
- Maintained backwards compatibility with existing code
- Modified both initial upload parsing and tailoring process to use LLM parsing

## Resume Parsing Flow
1. **Upload Phase**:
   - `upload_handler.py` receives resume file
   - If LLM parsing is enabled, `llm_resume_parser.py` processes the file
   - LLM receives the entire resume text and returns structured JSON
   - Parsed sections are mapped to UI-compatible format
   - Preview HTML is generated and rendered
   - If LLM parsing fails, traditional parsing is used

2. **Tailoring Phase**:
   - `claude_integration.py` retrieves the resume file
   - LLM parser is used again to ensure consistent section extraction
   - Each section is sent to the tailoring LLM with job requirements
   - Tailored sections are combined into a complete document

3. **File Structure**:
   - Original resume: `uuid.docx`
   - LLM parsing cache: `uuid_llm_parsed.json`
   - Traditional parsing cache: `uuid_analysis.json`
   - Formatted resume: `uuid_formatted.docx`
   - Tailored resume: `uuid_formatted_tailored_claude.docx` or `uuid_formatted_tailored_openai.docx`

## Job Parser Improvements
- Added comprehensive section extraction for LinkedIn and generic job postings
- Created intelligent section detection system to capture all major sections ("About the job", "Requirements", etc.)
- Improved bullet point extraction with support for various formats and symbols
- Enhanced skills detection with expanded vocabulary including modern AI/ML skills
- Structured response to include full sections alongside extracted requirements
- Added special handling for "About the job" section to ensure it's always captured

## Claude and OpenAI API Integration
- Switched from direct HTTP requests to official SDKs for both APIs
- Added robust error handling and logging of API calls
- Improved environment variable handling to prevent API key issues
- Created more effective prompting for bold, significant changes in tailored content
- Fixed serialization issues when handling API responses
- Added configurable provider selection (auto, claude, openai)
- Auto-detection of available API keys when using "auto" setting

## UI Improvements
- Reorganized the layout to show the "User Resume Parsed" and "Job Requirements" panels side by side in a dedicated row
- Enhanced card styling for consistent heights and better visual alignment
- Ensured responsive design for mobile devices
- Added proper scrolling behavior for content overflow
- Maintained the original step-based workflow with clear visual separation
- Added LLM indicator to parsed resume preview

## Latest Status
- Application is successfully parsing LinkedIn job listings with comprehensive section extraction
- LLM-based resume parsing is working correctly with multiple resume formats
- OpenAI and Claude API integration properly configured and working for resume tailoring
- Resume preview shows the tailored content with significant improvements
- All known blocking issues have been resolved and the application is functioning as expected

## Environment
- Python 3.x
- Flask web framework
- Claude API (via official Anthropic SDK) for AI-based resume tailoring
- OpenAI API (via official SDK) as an alternative LLM provider
- Required packages in requirements.txt

## Setup Notes
- Requires API key in .env file (Claude API key, OpenAI API key, or both)
- Flask SECRET_KEY must be set in .env
- LLM resume parsing configuration in .env:
  - USE_LLM_RESUME_PARSING=true
  - LLM_RESUME_PARSER_PROVIDER=auto
- Run with `python app.py`
- Accessible at http://localhost:5000 or https://localhost:5000 if certificates are available
- Required dependencies: flask, python-dotenv, requests, beautifulsoup4, python-docx, werkzeug, docx2txt, PyPDF2, pdfminer.six, flask-cors, anthropic, openai

# Instructions

During your interaction with the user, if you find anything reusable in this project (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the `Lessons` section in the `.cursorrules` file so you will not make the same mistake again. 

You should also use the `.cursorrules` file as a Scratchpad to organize your thoughts. Especially when you receive a new task, you should first review the content of the Scratchpad, clear old different task if necessary, first explain the task, and plan the steps you need to take to complete the task. You can use todo markers to indicate the progress, e.g.
[X] Task 1
[ ] Task 2

Also update the progress of the task in the Scratchpad when you finish a subtask.
Especially when you finished a milestone, it will help to improve your depth of task accomplishment to use the Scratchpad to reflect and plan.
The goal is to help you maintain a big picture as well as the progress of the task. Always refer to the Scratchpad when you plan the next step.

# Tools

Note all the tools are in python3. So in the case you need to do batch processing, you can always consult the python files and write your own script.

## Screenshot Verification

The screenshot verification workflow allows you to capture screenshots of web pages and verify their appearance using LLMs. The following tools are available:

1. Screenshot Capture:
```bash
venv/bin/python3 tools/screenshot_utils.py URL [--output OUTPUT] [--width WIDTH] [--height HEIGHT]
```

2. LLM Verification with Images:
```bash
venv/bin/python3 tools/llm_api.py --prompt "Your verification question" --provider {openai|anthropic} --image path/to/screenshot.png
```

Example workflow:
```python
from screenshot_utils import take_screenshot_sync
from llm_api import query_llm

# Take a screenshot

screenshot_path = take_screenshot_sync('https://example.com', 'screenshot.png')

# Verify with LLM

response = query_llm(
    "What is the background color and title of this webpage?",
    provider="openai",  # or "anthropic"
    image_path=screenshot_path
)
print(response)
```

## LLM

You always have an LLM at your side to help you with the task. For simple tasks, you could invoke the LLM by running the following command:
```
venv/bin/python3 ./tools/llm_api.py --prompt "What is the capital of France?" --provider "anthropic"
```

The LLM API supports multiple providers:
- OpenAI (default, model: gpt-4o)
- Azure OpenAI (model: configured via AZURE_OPENAI_MODEL_DEPLOYMENT in .env file, defaults to gpt-4o-ms)
- DeepSeek (model: deepseek-chat)
- Anthropic (model: claude-3-sonnet-20240229)
- Gemini (model: gemini-pro)
- Local LLM (model: Qwen/Qwen2.5-32B-Instruct-AWQ)

But usually it's a better idea to check the content of the file and use the APIs in the `tools/llm_api.py` file to invoke the LLM if needed.

## Web browser

You could use the `tools/web_scraper.py` file to scrape the web.
```bash
venv/bin/python3 ./tools/web_scraper.py --max-concurrent 3 URL1 URL2 URL3
```
This will output the content of the web pages.

## Search engine

You could use the `tools/search_engine.py` file to search the web.
```bash
venv/bin/python3 ./tools/search_engine.py "your search keywords"
```
This will output the search results in the following format:
```
URL: https://example.com
Title: This is the title of the search result
Snippet: This is a snippet of the search result
```
If needed, you can further use the `web_scraper.py` file to scrape the web page content.

# Lessons

## Project-Specific Lessons
- Always ensure Claude API Key is properly configured in .env file
- Use official Anthropic SDK for Claude API integration
- When parsing job listings, use comprehensive section detection to capture all relevant sections
- Initialize empty sections in resume data structures to avoid KeyError
- For regex patterns in job_parser.py, ensure proper escaping of special characters
- When generating resume previews, properly handle bullet points (•, -, *) for better formatting
- Log the actual Claude API responses for debugging and transparency
- When creating DOCX documents, use correct paragraph styles (Heading 1, Heading 2, List Bullet) for proper formatting
- In generate_resume_preview function, check for bullet point markers and create proper HTML list elements
- Ensure the proper use of section headers in the document to create well-structured resumes
- When testing API functionality, create standalone test scripts that can verify each part of the workflow
- Split document creation from content tailoring for cleaner code organization
- Implement robust resume section extraction with multiple detection approaches:
  - Use both paragraph style and text formatting (bold) to identify potential section headers
  - Expand regex patterns for section detection to catch various naming conventions (e.g., "about" for summary)
  - Default new documents to "contact" section rather than "header" to ensure content is properly categorized
  - Log potential section headers for easier debugging of parsing issues
  - Implement fallback mechanisms that process the entire document when standard detection fails
  - Always return a structured response even when extraction fails to prevent KeyErrors downstream
- Add detailed logging throughout the resume parsing process to quickly identify extraction issues
- Be aware that resume formats vary widely; some may not use standard headings or formatting
- Count the total paragraphs with content to validate that document parsing is working correctly
- Consider multiple stages of parsing in a web application:
  - Initial upload parsing requires different handling than later processing
  - Modify both stages to use the same parsing logic for consistency
  - Map between different data structures when necessary
- When implementing LLM-based parsing:
  - Use low temperature (0.1) for consistent, deterministic results
  - Include clear, specific instructions about expected output format
  - Implement JSON parsing fallbacks for malformed responses
  - Add robust validation to verify the expected structure is present
  - Always have a traditional fallback method ready
- For multiple LLM provider support:
  - Implement provider-specific classes or methods
  - Use environment variables for configuration
  - Add auto-detection of available API keys
  - Maintain consistent input/output formats across providers

## User Specified Lessons
- You have a python venv in ./venv. Always use (activate) it when doing python development. First, to check whether 'uv' is available, use `which uv`. If that's the case, first activate the venv, and then use `uv pip install` to install packages. Otherwise, fall back to `pip`.
- Due to Cursor's limit, when you use `git` and `gh` and need to submit a multiline commit message, first write the message in a file, and then use `git commit -F <filename>` or similar command to commit. And then remove the file. Include "[Cursor] " in the commit message and PR title.

## Cursor learned
- For search results, ensure proper handling of different character encodings (UTF-8) for international queries
- When using seaborn styles in matplotlib, use 'seaborn-v0_8' instead of 'seaborn' as the style name due to recent seaborn version changes
- Use 'gpt-4o' as the model name for OpenAI's GPT-4 with vision capabilities
- When searching for recent news, use the current year (2025) instead of previous years, or simply use the "recent" keyword to get the latest information
- When working with PowerShell on Windows, use `;` instead of `&&` for command chaining
- For parsing HTML content in resumes, pay attention to nested elements and formatting
- When importing Python modules from external sources, ensure they're properly installed in the environment
- Check for WD_ALIGN_PARAGRAPH usage from docx library for document formatting

# Scratchpad 

## Resume Tailoring Improvements - April 13, 2025

[X] Integrate devin.cursorrules repository
  - Cloned repository into devin/ folder
  - Copied tools directory and its scripts
  - Updated .cursorrules file with combined content
  - Added dependencies to requirements.txt
  - Updated .env file with new API keys

[X] Fix resume preview issues
  - Improved document structure in DOCX generation
  - Enhanced HTML preview rendering 
  - Added proper formatting for bullet points
  - Created proper section headers

[X] Add Claude API logging
  - Now storing complete API responses
  - Added request/response data with timestamps
  - Included token usage statistics

[X] Create test scripts
  - Direct Claude API testing
  - End-to-end workflow testing
  - HTML preview testing
  - HTTP API testing

[X] Document progress and lessons learned
  - Updated .cursorrules with new lessons
  - Created commit message
  - Added detailed Scratchpad notes

## Resume Section Parsing Improvements - April 15, 2025

[X] Fixed critical resume section extraction issues
  - Enhanced regex patterns to detect various section naming conventions
  - Added detailed logging of potential section headers for debugging
  - Implemented fallback mechanism for documents with non-standard formatting
  - Created robust error handling to prevent downstream failures
  - Fixed default section from "header" to "contact" for better initial content categorization
  
[X] Improved debugging and visibility
  - Added paragraph counting to validate document parsing
  - Logged detailed section detection process for transparency
  - Created comprehensive section detection report in logs
  - Added fallback mechanism that treats content as experience section when headers aren't detected

[X] Tested with various resume formats
  - Successfully processed resume with non-standard formatting
  - Verified that tailored content is properly generated when sections are extracted
  - Confirmed that the fallback mechanism works correctly when standard detection fails

## LLM Resume Parsing Implementation - April 15, 2025

[X] Created LLM-based resume parsing module
  - Implemented `llm_resume_parser.py` with `LLMResumeParser` class
  - Added support for both Claude and OpenAI APIs
  - Created detailed prompting for accurate section extraction
  - Implemented robust validation and error handling

[X] Integrated LLM parsing with existing code
  - Updated `claude_integration.py` to use LLM parsing for tailoring
  - Modified `upload_handler.py` to use LLM parsing for initial upload
  - Added mapping between different data structures for compatibility
  - Maintained fallback to traditional parsing when needed

[X] Added configuration and environment support
  - Created toggle for LLM parsing in `config.py`
  - Added provider selection (auto, claude, openai)
  - Implemented auto-detection of available API keys
  - Added new variables to `.env` file

[X] Enhanced logging and caching
  - Added detailed logging throughout the parsing process
  - Created JSON caching to avoid repeated API calls
  - Added token usage and processing time tracking
  - Implemented clear success/failure indicators

Next steps:
- Add confidence scores to LLM parsing results
- Create resume format validator to help prepare optimal resumes
- Add visual diff feature to highlight tailoring changes  
- Enhance UI to better display tailored sections
- Implement few-shot learning with example resumes for improved parsing

## LLM Job Analysis Implementation - April 16, 2025

[X] Created LLM-based job analysis module
  - Implemented `llm_job_analyzer.py` module with comprehensive job analysis functionality
  - Created prompt template to extract candidate profile, hard/soft skills, and ideal candidate
  - Added support for both Claude and OpenAI APIs with auto-selection
  - Implemented JSON output format for structured analysis

[X] Integrated job analysis into the workflow
  - Modified `job_parser.py` to use LLM for enhanced job understanding
  - Added new endpoint `/api/analyze-job` for dedicated job analysis
  - Updated `job_parser_handler.py` to process and return LLM analysis results
  - Created caching mechanism to avoid repeated API calls for the same job

[X] Enhanced user interface for job analysis
  - Added dedicated "AI Analysis" section with distinctive styling
  - Created CSS styles with purple color theme for AI insights
  - Added visual components for candidate profile, hard/soft skills, and ideal candidate
  - Implemented fallback to basic parsing if LLM analysis fails

[X] Added OpenAI-only mode support
  - Modified frontend code to use OpenAI explicitly when Claude is unavailable
  - Updated default provider selection to prioritize OpenAI
  - Modified job analysis to work effectively with OpenAI's gpt-4o model
  - Added better error handling for API authentication issues
  - Improved logging of API responses and token usage

[X] Testing and validation
  - Confirmed proper analysis of LinkedIn job listings
  - Verified integration with the tailoring workflow
  - Ensured both Claude and OpenAI providers work correctly
  - Created comprehensive logging of the analysis process
  - Confirmed the enhanced tailoring results using the job analysis

Next steps:
- Create visual diff to highlight changes between original and tailored resume
- Add confidence scores to LLM analysis results
- Implement few-shot learning with example job postings
- Add section-specific prompts for more accurate job analysis

## YC-Eddie Style Resume Implementation - April 16, 2025

[X] Created YC-Eddie style resume formatter
  - Implemented dedicated resume_styler.py module
  - Created YCEddieStyler class for consistent document styling
  - Added professional formatting with proper margins and spacing
  - Implemented consistent section header styling with underlines
  - Applied proper bullet point formatting for experience items

[X] Enhanced document generation process
  - Modified claude_integration.py to use new styler
  - Created brand new documents instead of using templates
  - Applied consistent formatting across all sections
  - Fixed issues with bullet point rendering
  - Added proper spacing between sections

[X] Fixed tailored resume preview display
  - Updated JavaScript to properly handle the tailored resume preview
  - Separated user resume preview from tailored resume preview
  - Added proper formatting to HTML preview
  - Fixed display issues that prevented tailored content from showing
  - Added automatic scrolling to the tailored preview section

[X] Integrated with existing workflow
  - Made styler compatible with both Claude and OpenAI responses
  - Added detailed logging for document creation process
  - Preserved all tailored content with improved formatting
  - Tested with real job listings and resumes
  - Confirmed proper rendering in downloaded DOCX file

## Next Steps
- Implement achievement-focused prompt optimization
- Create visual diff feature to highlight tailoring changes
- Add confidence scores to LLM parsing results
- Enhance UI with more professional styling
- Implement few-shot learning with example resumes

## PythonAnywhere Deployment - April 17, 2025

[X] Successfully deployed the application on PythonAnywhere
  - Created a PythonAnywhere account and set up a web application
  - Cloned the repository using GitHub Personal Access Token
  - Configured the virtual environment with essential packages
  - Set up WSGI file with proper environment variables and app import
  - Added static file mappings for CSS, JavaScript, and uploads
  - Created uploads directory for file storage
  - Enabled HTTPS by default

[X] Troubleshooted common deployment issues
  - Resolved GitHub authentication using Personal Access Token
  - Addressed disk quota limitations by installing only essential packages
  - Fixed Python version mismatch between virtualenv and web app
  - Added environment variables directly to WSGI file
  - Replaced default Hello World WSGI file with proper configuration

[X] Documented the deployment process
  - Created comprehensive site_deployment_lessons.md guide
  - Documented all steps required to deploy on PythonAnywhere
  - Added troubleshooting tips for common issues
  - Included instructions for custom domain setup
  - Added performance and security considerations

[X] Created domain setup for jobsculptor.ai
  - Added domain in PythonAnywhere web app configuration
  - Prepared DNS configuration instructions
  - Documented steps for connecting custom domain

Next steps:
- Monitor application performance on PythonAnywhere
- Consider upgrading to paid tier if CPU quota becomes limiting
- Implement secure environment variable storage
- Set up periodic backups of uploaded resumes
- Add analytics to track usage patterns
# Resume Tailoring Website Using LLM Technology

## Project Overview
This application helps users tailor their resumes to match specific job listings using Claude AI. The application analyzes job postings, extracts requirements, and optimizes the resume accordingly.

## Files and Structure
- **app.py**: Main Flask application entrypoint
- **config.py**: Configuration settings (API keys, upload paths)
- **upload_handler.py**: Handles resume file uploads
- **resume_processor.py**: Processes and analyzes uploaded resumes
- **resume_formatter.py**: Formats resumes into a standardized structure
- **job_parser.py**: Parses job listings from URLs (LinkedIn and generic)
- **claude_integration.py**: Interfaces with Claude AI for resume tailoring
- **tailoring_handler.py**: Orchestrates the tailoring process
- **format_handler.py**: API routes for resume formatting
- **job_parser_handler.py**: API routes for job parsing
- **static/css/styles.css**: Styling for the application
- **static/js/main.js**: Frontend JavaScript
- **templates/index.html**: Main HTML interface
- **static/uploads/**: Stores uploaded and processed files

## Input/Output Flow
1. **Input**: User uploads DOCX resume and provides job listing URL
2. **Processing**: 
   - Resume is formatted into standardized structure
   - Job listing is parsed to extract requirements and skills
   - Claude AI tailors resume content to match job requirements
3. **Output**: Tailored resume available for download as DOCX

## Fixes Applied
1. Added proper secret key for Flask app security
2. Created correct folder structure for Flask app (templates/, static/)
3. Fixed template_resume.docx path issue by copying to static/uploads directory
4. Fixed 'summary' KeyError by properly initializing empty sections
5. Enhanced section handling to properly check for empty content before processing
6. Fixed regex character range error in job_parser.py that was causing LinkedIn job parsing to fail
7. Fixed demo mode vs. API mode by ensuring the Claude API key is properly configured
8. Added .env and sensitive files to .gitignore to prevent exposing API keys
9. Improved UI layout by aligning "User Resume Parsed" and "Job Requirements" panels side by side
10. Made HTTP/HTTPS dynamic based on certificate availability
11. Ensured proper dependency installation for PDF and DOCX processing
12. Significantly improved job parsing to capture "About the job" and all relevant sections
13. Enhanced section detection in job listings using advanced pattern matching
14. Fixed Claude API integration to properly use official Anthropic SDK
15. Removed demo mode fallback to ensure consistent API usage and testing

## Job Parser Improvements
- Added comprehensive section extraction for LinkedIn and generic job postings
- Created intelligent section detection system to capture all major sections ("About the job", "Requirements", etc.)
- Improved bullet point extraction with support for various formats and symbols
- Enhanced skills detection with expanded vocabulary including modern AI/ML skills
- Structured response to include full sections alongside extracted requirements
- Added special handling for "About the job" section to ensure it's always captured

## Claude API Integration Fixes
- Switched from direct HTTP requests to official Anthropic Python SDK
- Added robust error handling and logging of API calls
- Improved environment variable handling to prevent API key issues
- Created more effective prompting for bold, significant changes in tailored content
- Fixed serialization issues when handling Claude API responses

## UI Improvements
- Reorganized the layout to show the "User Resume Parsed" and "Job Requirements" panels side by side in a dedicated row
- Enhanced card styling for consistent heights and better visual alignment
- Ensured responsive design for mobile devices
- Added proper scrolling behavior for content overflow
- Maintained the original step-based workflow with clear visual separation

## Latest Status
- Application is successfully parsing LinkedIn job listings with comprehensive section extraction
- Claude API integration is properly configured and working for resume tailoring
- Job parser now captures the complete job description including "About the job" sections
- Resume preview shows the Claude AI tailored content with significant improvements
- All known blocking issues have been resolved and the application is functioning as expected

## Environment
- Python 3.x
- Flask web framework
- Claude API (via official Anthropic SDK) for AI-based resume tailoring
- Required packages in requirements.txt

## Setup Notes
- Requires Claude API key in .env file
- Flask SECRET_KEY must be set in .env
- Run with `python app.py`
- Accessible at http://localhost:5000 or https://localhost:5000 if certificates are available
- Required dependencies: flask, python-dotenv, requests, beautifulsoup4, python-docx, werkzeug, docx2txt, PyPDF2, pdfminer.six, flask-cors, anthropic 
