# Resume Tailor Project Context

## Project Overview
The Resume Tailor is an AI-powered application that helps users customize their resumes for specific job postings. It uses Claude or OpenAI to analyze job listings and tailor resumes to highlight relevant skills and experience. The application provides a professional PDF output with consistent formatting based on YC-Eddie style guidelines.

## Repository Details
- **GitHub Repository**: https://github.com/nanaoosaki/manus_resume_site
- **Current Branch**: main
- **Local Development Path**: D:\AI\manus_resumeTailor

## Deployment Status
- **Deployed At**: PythonAnywhere (free tier)
- **Domain**: jobsculptor.ai
- **Deployment Date**: April 17, 2025
- **Special Notes**: Using system Python (no virtualenv) due to disk quota limitations

## Key Features Implemented
1. **Resume Parsing**: LLM-based resume parsing with traditional fallback
2. **Job Analysis**: Extracts requirements, skills, and candidate profiles from job listings
3. **Resume Tailoring**: Customizes each resume section based on job requirements
4. **YC-Eddie Style Formatting**: Creates clean, professional resume documents with modern styling (centered headers with box borders and dot bullet points)
5. **Preview Generation**: Shows HTML preview of tailored resumes with consistent styling
6. **Multi-Provider Support**: Works with both OpenAI and Claude APIs
7. **PDF Export**: Generates professionally formatted PDF documents instead of Word documents
8. **A4 Paper Format**: Implemented A4 paper format for HTML preview matching PDF output

## Technologies and APIs
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Document Processing**: python-docx, docx2txt, WeasyPrint (for PDF generation)
- **LLM Providers**: 
  - Claude (Anthropic) - Primary
  - OpenAI (GPT-4o) - Fallback
- **Job Source Support**: LinkedIn and generic job listings

## Recent Changes and Fixes
1. **Template Dependency Removed**: Eliminated reliance on template_resume.docx
2. **Resume Preview Fixed**: Separated user resume and tailored resume previews
3. **LLM Resume Parsing**: Added sophisticated document parsing with LLMs
4. **Deployment Optimized**: Modified for PythonAnywhere free tier constraints
5. **Job Analysis Enhanced**: Added comprehensive job requirement extraction
6. **Modern Resume Styling**: Updated document formatting with centered box headers and dot bullet points
7. **HTML Preview Alignment**: Ensured consistent styling between documents and HTML previews
8. **PDF Export**: Switched from Word document generation to PDF export for better consistency
9. **A4 Paper Format**: Implemented proper A4 paper dimensions with 1-inch margins for HTML preview
10. **Contact Information Fix**: Attempted to ensure contact information is preserved in tailored resumes

## Current Limitations and Known Issues
1. **PythonAnywhere Constraints**: 
   - 512MB disk quota on free tier
   - CPU time limitations (100 seconds/day)
2. **Large Resume Handling**: Very large resumes (>20 pages) may exceed token limits
3. **Custom Formatting**: Limited support for highly customized resume formats
4. **Contact Information Missing**: Contact information may not be preserved in tailored resume output
5. **Company/Location Separation**: Difficulty separating company names from locations in some formats
6. **Bullet Point Duplication**: Some bullet points appear duplicated in the final output

## File Structure and I/O Details

### Core Application Files
- **app.py**: 
  - Main Flask application
  - **Input**: HTTP requests, form submissions
  - **Output**: HTML responses, redirects, file downloads
  - **Dependencies**: All other modules

- **config.py**: 
  - Configuration settings
  - **Input**: Environment variables
  - **Output**: Configuration constants and settings
  - **Used by**: All other modules

### Resume Processing
- **resume_processor.py**: 
  - Handles resume file upload and basic parsing
  - **Input**: DOCX files, PDF files
  - **Output**: Parsed resume content, JSON cache files
  - **Used by**: app.py, upload_handler.py

- **llm_resume_parser.py**: 
  - LLM-based resume parsing
  - **Input**: Resume text content, LLM provider selection
  - **Output**: Structured resume sections, cached parsing data
  - **Used by**: claude_integration.py, resume_processor.py

### Job Analysis
- **job_parser.py**: 
  - Job listing extraction
  - **Input**: LinkedIn URLs, general job URLs
  - **Output**: Structured job details, requirements
  - **Used by**: app.py, job_parser_handler.py

- **llm_job_analyzer.py**: 
  - LLM-based job posting analysis
  - **Input**: Job posting text, LLM provider selection
  - **Output**: Structured job analysis, candidate profile, skills
  - **Used by**: job_parser.py

### Resume Tailoring
- **claude_integration.py**: 
  - LLM integration for tailoring
  - **Input**: Resume sections, job details, API keys
  - **Output**: Tailored resume content
  - **Used by**: tailoring_handler.py, app.py

- **tailoring_handler.py**: 
  - Orchestrates the tailoring process
  - **Input**: Resume path, job data, API provider
  - **Output**: Tailored document, preview HTML
  - **Used by**: app.py

### Document Generation
- **resume_styler.py**: 
  - YC-Eddie style resume formatter
  - **Input**: Tailored section content
  - **Output**: Formatted Word document
  - **Used by**: claude_integration.py, tailoring_handler.py

- **pdf_exporter.py**: 
  - Converts HTML to PDF
  - **Input**: HTML resume content
  - **Output**: PDF document
  - **Used by**: tailoring_handler.py

### Frontend
- **templates/index.html**: 
  - Main application interface
  - Handles user interactions
  - **Input**: User actions
  - **Output**: Visual interface

- **static/css/styles.css**: 
  - Main stylesheet for UI
  - **Used by**: index.html

- **static/css/pdf_styles.css**: 
  - Styles specific to PDF output
  - **Used by**: pdf_exporter.py

- **static/js/main.js**: 
  - Frontend JavaScript
  - Handles AJAX requests, UI updates
  - **Input**: User actions, server responses
  - **Output**: DOM updates
  - **Used by**: index.html

## Application Workflow

### 1. Resume Upload Process
1. User uploads resume (DOCX/PDF) via web interface
2. `app.py` receives the file and passes it to `resume_processor.py`
3. `resume_processor.py` saves the file and initiates parsing
4. `llm_resume_parser.py` attempts to parse the resume with LLM:
   - If successful, returns structured sections
   - If fails, falls back to traditional parsing
5. Parsed resume sections are displayed in the UI
6. Resume data is cached for future use

### 2. Job Parsing Process
1. User enters a job URL via web interface
2. `app.py` passes the URL to `job_parser.py`
3. `job_parser.py` extracts job listing content:
   - For LinkedIn, uses specific scraping techniques
   - For other sites, uses generic extraction
4. `llm_job_analyzer.py` analyzes the job content to extract:
   - Candidate profile
   - Hard skills required
   - Soft skills valued
   - Ideal candidate description
5. Job requirements and analysis are displayed in the UI
6. Job data is cached for future use

### 3. Resume Tailoring Process
1. User requests tailoring via web interface
2. `app.py` triggers `tailoring_handler.py`
3. `tailoring_handler.py` coordinates:
   - Getting resume sections from cache or re-parsing
   - Getting job details from cache or re-parsing
   - Calling LLM integration
4. `claude_integration.py` performs section-by-section tailoring:
   - Each section sent to Claude/OpenAI with specific prompts
   - Content optimized for job requirements
   - Contact information preserved without changes
5. `generate_preview_from_llm_responses` creates HTML preview
6. HTML preview displayed to user in the UI
7. When download requested, `pdf_exporter.py` converts HTML to PDF

### 4. PDF Export Process
1. User clicks "Download Tailored Resume"
2. `app.py` triggers PDF generation
3. `pdf_exporter.py`:
   - Takes HTML content from preview
   - Applies PDF-specific styles
   - Uses WeasyPrint to convert HTML to PDF
4. PDF file is sent to user's browser for download

## Current Development Focus
1. **Contact Information Preservation**: Fixing issues with contact details in tailored resumes
2. **HTML Preview Enhancement**: Ensuring HTML preview precisely matches PDF output
3. **Bullet Point Formatting**: Resolving inconsistencies in bullet point display
4. **Company/Location Separation**: Improving the accuracy of entity recognition
5. **PDF Format Optimization**: Fine-tuning A4 paper layout and margins

## Future Roadmap
1. **Visual Diff Feature**: Highlight changes between original and tailored resume
2. **Resume Format Validator**: Help prepare optimal resumes before tailoring
3. **Confidence Scores**: Add confidence metrics to LLM parsing results
4. **Alternative LLM Providers**: Implement backup providers for resilience
5. **User Accounts**: Save tailoring history and multiple resumes
6. **Resume Scoring**: Analyze resume against job requirements
7. **Bulk Processing**: Support tailoring for multiple job listings at once

## To Include in Future Conversations
When starting new conversations with Claude about this project, include this file and mention:
1. You're working on the Resume Tailor application
2. Reference recent changes you've made
3. Specify which part of the application you're focusing on
4. Indicate if you're working on local development or deployment 