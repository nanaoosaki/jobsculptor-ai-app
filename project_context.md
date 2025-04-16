# Resume Tailor Project Context

## Project Overview
The Resume Tailor is an AI-powered application that helps users customize their resumes for specific job postings. It uses Claude or OpenAI to analyze job listings and tailor resumes to highlight relevant skills and experience.

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
4. **YC-Eddie Style Formatting**: Creates clean, professional resume documents with modern styling (centered headers with box borders and arrow bullet points)
5. **Preview Generation**: Shows HTML preview of tailored resumes with consistent styling
6. **Multi-Provider Support**: Works with both OpenAI and Claude APIs

## Technologies and APIs
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Document Processing**: python-docx, docx2txt
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
6. **Modern Resume Styling**: Updated document formatting with centered box headers and arrow bullet points
7. **HTML Preview Alignment**: Ensured consistent styling between Word documents and HTML previews

## Current Limitations
1. **PythonAnywhere Constraints**: 
   - 512MB disk quota on free tier
   - CPU time limitations (100 seconds/day)
2. **Large Resume Handling**: Very large resumes (>20 pages) may exceed token limits
3. **Custom Formatting**: Limited support for highly customized resume formats

## File Structure Overview
- **app.py**: Main Flask application
- **config.py**: Configuration settings
- **claude_integration.py**: LLM integration for tailoring
- **resume_styler.py**: YC-Eddie style resume formatter
- **llm_resume_parser.py**: LLM-based resume parsing
- **job_parser.py**: Job listing extraction
- **tailoring_handler.py**: Orchestrates the tailoring process

## Development Status
- Core functionality complete and working
- Actively improving job parsing accuracy
- Enhancing resume preview visualization
- Optimizing for PythonAnywhere deployment
- Adding visual diff to highlight changes between original and tailored resume

## To Include in Future Conversations
When starting new conversations with Claude about this project, include this file and mention:
1. You're working on the Resume Tailor application
2. Reference recent changes you've made
3. Specify which part of the application you're focusing on
4. Indicate if you're working on local development or deployment 