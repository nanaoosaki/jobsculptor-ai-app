# Resume Tailoring Application

AI-powered resume tailoring tool that analyzes job postings and optimizes resumes to match job requirements using Claude AI.

## Debugging Tasks

### File Path Issue in HTML Generator (FIXED)

**Issue Description:**
When running the application after reorganizing files, we discovered a path resolution problem between the file saving and file reading operations. The HTML preview is empty but the PDF generation succeeds.

**Symptoms:**
- JSON files are successfully saved by claude_integration.py:
  ```
  INFO:claude_integration:Saved experience content to D:\AI\manus_resume3\static/uploads\api_responses\experience.json
  ```
- HTML generator fails to find these files:
  ```
  ERROR:html_generator:Error processing experience section: [Errno 2] No such file or directory: 'uploads\\api_responses\\experience.json'
  ```

**Root Cause Analysis:**
1. Path inconsistency: claude_integration.py saves files using absolute paths with forward slashes, while html_generator.py tries to read them using relative paths with backslashes.
2. Directory structure: html_generator.py is looking for files in 'uploads\\api_responses\\' but they're being saved to 'static/uploads\api_responses\'.
3. The inconsistent use of slashes vs. backslashes (/ vs \) is also contributing to the issue.
4. The education and projects sections were being saved as raw strings in JSON files, which caused parsing errors when the HTML generator tried to read them.

**Applied Fixes:**
1. Updated html_generator.py to use the same path construction logic as claude_integration.py:
   ```python
   # Find the response files directory - use consistent path with claude_integration.py
   api_responses_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_responses')
   ```

2. Added proper logging to track path usage:
   ```python
   logger.info(f"Looking for API responses in: {api_responses_dir}")
   ```

3. Added directory creation if it doesn't exist:
   ```python
   if not os.path.exists(api_responses_dir):
       logger.warning(f"API responses directory not found, creating: {api_responses_dir}")
       os.makedirs(api_responses_dir)
   ```

4. Updated claude_integration.py to ensure all sections are saved in proper JSON format:
   ```python
   # For education and projects, convert to proper JSON format (not raw string)
   json_data = {"content": content}
   
   # Write to file - always use json.dump, not raw strings
   with open(filepath, 'w', encoding='utf-8') as f:
       json.dump(json_data, f, indent=2)
   ```

5. Enhanced error handling in format_education_content and format_projects_content to handle both JSON and raw string content:
   ```python
   try:
       # Try to parse as JSON first
       if content.strip().startswith('{') or content.strip().startswith('['):
           try:
               data = json.loads(content)
               # Process structured JSON data
               # ...
           except json.JSONDecodeError:
               # If JSON parsing fails, treat as raw content
               return format_section_content(content)
       else:
           # Treat as raw content
           return format_section_content(content)
   except Exception as e:
       logger.error(f"Error formatting content: {str(e)}")
       return f"<p>Error formatting section: {str(e)}</p>"
   ```

**Results:**
- Fixed the path resolution issue between claude_integration.py and html_generator.py
- Fixed the JSON parsing errors for education and projects sections
- The HTML preview and PDF generation now work as expected
- The only remaining expected error is for the summary section which doesn't exist in most resumes

## Completed Tasks

- [x] Set up basic Flask application structure
- [x] Create resume upload and parsing functionality
- [x] Implement job listing parser for LinkedIn and generic URLs
- [x] Integrate Claude AI for resume tailoring 