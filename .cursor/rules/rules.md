# Resume Tailoring Project Guidelines

## Project Context
This file contains guidelines for the Resume Tailoring application (JobSculptor.ai), which helps users customize their resumes for specific job postings using LLM technology.

## File Structure
The guidelines and context for this project are organized in the following files:
- `.cursor/rules/context.md` - Full project context (merged from previous .cursorrules and .cursorules files)
- `.cursor/rules/rules.md` - This file, containing core guidelines and references
- `.cursor/task-list.mdc` - Current task list for the project

## Repository Details
- **GitHub Repository**: https://github.com/nanaoosaki/manus_resume_site
- **Current Branch**: main
- **Local Development Path**: D:\AI\manus_resumeTailor
- **Deployment**: PythonAnywhere (free tier)
- **Domain**: jobsculptor.ai

## Development Guidelines
1. Always activate the Python virtual environment before development
2. Ensure proper error handling throughout the application
3. Implement robust fallback mechanisms when using LLM API calls
4. Follow established code patterns for consistency
5. Document all significant changes in the codebase
6. Test with various resume formats and job listings

## Cursor-Specific Instructions
When using Cursor with this project:
1. Refer to the context in `.cursor/rules/context.md` for comprehensive project information
2. Update `.cursor/task-list.mdc` when tasks are completed
3. Document lessons learned and technical details in `.cursor/rules/context.md`
4. Use the Scratchpad in `.cursor/rules/context.md` to organize thoughts and planning

## Current Development Focus
- Optimizing tailoring prompts for achievement-focused content
- Creating a resume format validator
- Adding visual diff feature to highlight changes
- Implementing confidence scores for LLM parsing results
- Enhancing PythonAnywhere deployment efficiency