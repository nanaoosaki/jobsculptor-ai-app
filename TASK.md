# Resume Tailoring Application

AI-powered resume tailoring tool that analyzes job postings and optimizes resumes to match job requirements using Claude AI.

## Completed Tasks

- [x] Set up basic Flask application structure
- [x] Create resume upload and parsing functionality
- [x] Implement job listing parser for LinkedIn and generic URLs
- [x] Integrate Claude AI for resume tailoring
- [x] Fix resume section parsing with enhanced regex patterns
- [x] Add fallback mechanism for non-standard resume formats
- [x] Improve error handling in resume parsing
- [x] Add detailed logging for debugging
- [x] Fix JavaScript to correctly display tailored resume
- [x] Implement LLM-based resume parsing with fallback mechanism
- [x] Integrate LLM parsing into initial resume upload process
- [x] Add configurable LLM provider selection (Claude/OpenAI)
- [x] Create JSON caching for parsed resume data
- [x] Improve job parser to extract complete job text for LLM processing
- [x] Update job parser UI to display complete job description
- [x] Implement LLM-based job posting analysis
- [x] Enhance UI to better display tailored sections with AI analysis highlights
- [x] Implement YC-Eddie Style resume format in document generation
- [x] Enhance resume styling with modern box borders and arrow bullet points
- [x] Update resume formatting with dot bullet points instead of arrows
- [x] Add horizontal line under contact information section
- [x] Remove bold font formatting from resume sections
- [x] Reduce line spacing between resume sections for better readability
- [x] Fix empty bullet points in tailored resume output
- [x] Add resume index system for tracking relationships between parsed resumes, LLM responses, and generated PDFs
- [x] Switch from Word document generation to PDF export for better consistency
- [x] Implement HTML-to-PDF conversion with professional styling
- [x] Update download functionality to provide PDF files instead of Word documents
- [x] Optimize PDF layout for ATS compatibility and professional appearance
- [x] Refactor `claude_integration.py` into smaller, more focused modules

## In Progress Tasks

- [x] Fix HTML layout shrinking issue after refactoring
- [ ] Fix empty HTML content issue after refactoring
- [ ] Optimize tailoring prompts for high-quality, achievement-focused content
- [ ] Create resume format validator to help prepare optimal resumes
- [ ] Add visual diff feature to highlight tailoring changes
- [ ] Add confidence scores to LLM parsing results
- [x] Implement session-based storage for multi-user environment

## Future Tasks

- [ ] Implement alternative LLM providers as fallback options
- [ ] Add job search functionality using search engine tools
- [ ] Create user accounts and save tailoring history
- [ ] Implement resume scoring against job requirements
- [ ] Add bulk processing of multiple job listings
- [ ] Implement few-shot learning with example resumes for improved parsing
- [ ] Add section-specific prompts for more accurate tailoring

## Implementation Plan

The resume tailoring application uses a Flask backend with a simple frontend interface. The core functionality revolves around:

1. Resume parsing and section extraction:
   - Uses python-docx to extract content from DOCX files
   - Identifies sections through heading styles and text formatting
   - Implements fallback mechanisms for non-standard formats
   
   **Enhanced LLM-based Resume Parsing:**
   - Integrate LLM (Claude/OpenAI) as the primary method for resume parsing
   - Send the entire resume content to LLM with a prompt to identify and categorize sections
   - Store parsed sections in a structured JSON format with section types as keys
   - Implement a fallback mechanism to use the existing regex/heading-based parser if:
     - LLM API call fails (network/authentication issues)
     - LLM response doesn't contain expected section structure
     - Timeout occurs during LLM processing
   - Cache LLM parsing results to avoid repeated API calls for the same resume
   - Add logging for both successful LLM parsing and fallbacks to traditional parsing
   - Create a configurable toggle to enable/disable LLM parsing for testing/development

2. Job listing parsing:
   - Scrapes job listings from LinkedIn and other URLs
   - Extracts requirements, skills, and job details
   - Formats job data for AI processing
   
   **Enhanced LLM-based Job Analysis:**
   - Integrate LLM (Claude/OpenAI) to intelligently analyze job postings
   - Send the complete job text to LLM with a prompt to extract structured insights
   - Have the LLM identify:
     - Candidate profile: What type of candidates the position is targeting
     - Hard skills: Technical and job-specific skills required
     - Soft skills: Personal and interpersonal skills valued
     - Ideal candidate: Comprehensive description of the perfect match
   - Return the analysis in structured JSON format for frontend consumption
   - Cache the LLM analysis results to avoid repeated API calls
   - Implement fallback to regex-based parsing if LLM analysis fails
   - Add logging for the analysis process and results
   - Add a configurable toggle to enable/disable LLM job analysis

3. AI-powered tailoring:
   - Uses Claude AI through Anthropic API or OpenAI API
   - Analyzes resume sections against job requirements
   - Generates tailored content that emphasizes relevant experience

4. Document generation:
   - Creates new DOCX files with tailored content
   - Preserves original formatting and structure
   - Provides downloadable files and HTML preview

## LLM Resume Parsing Implementation Details

1. **Parser Integration:**
   - Created `llm_resume_parser.py` module with the `LLMResumeParser` class
   - Modified `claude_integration.py` to attempt LLM parsing before traditional parsing
   - Modified `upload_handler.py` to use LLM parsing during initial resume upload
   - Used the same section structure to ensure compatibility between all methods

2. **Data Flow:**
   - Resume upload → LLM parsing → Section extraction → Display in UI
   - LLM parsing failures gracefully fall back to traditional parsing
   - Parsed resume data is cached as JSON files to avoid repeated API calls
   - Sections are immediately displayed in UI with proper categorization

3. **Configuration Options:**
   - `USE_LLM_RESUME_PARSING` - Enable/disable LLM parsing (default: true)
   - `LLM_RESUME_PARSER_PROVIDER` - Select LLM provider (auto, claude, openai)
   - Auto-detection of available API keys when provider is set to "auto"

4. **LLM Prompt Design:**
   - Clear instructions for section identification without adding/changing content
   - Specific output format requirements to ensure consistent JSON structure
   - Low temperature (0.1) for deterministic, precise output
   - Explicit handling of each resume section type

## LLM Job Analysis Implementation Details

1. **Analyzer Integration:**
   - Created new `llm_job_analyzer.py` module with job analysis functions
   - Added a prompt template designed to extract structured insights from job postings
   - Integrated analysis into the job parsing workflow through `job_parser.py`
   - Modified `job_parser_handler.py` to include LLM analysis in the response

2. **Data Flow:**
   - Job URL submission → Traditional parsing → Complete text extraction → LLM analysis → UI display
   - LLM analysis failures gracefully fall back to traditional parsing
   - Analyzed job data cached as JSON files to avoid repeated API calls
   - Analysis results displayed in UI alongside other job information

3. **Configuration Options:**
   - `USE_LLM_JOB_ANALYSIS` - Enable/disable LLM job analysis (default: true)
   - `LLM_JOB_ANALYZER_PROVIDER` - Select LLM provider (auto, claude, openai)
   - Auto-detection of available API keys when provider is set to "auto"

4. **LLM Prompt Design:**
   - Clear instructions for extracting specific insights from job postings
   - Structured output format with sections for different aspects of analysis
   - Low temperature (0.1) for deterministic, precise output
   - Consistent JSON output structure for frontend consumption

5. **UI Integration:**
   - Added a dedicated "AI Analysis" section at the top of job requirements
   - Used purple color theme to distinguish AI insights from regular content
   - Created visual components for candidate profile, hard skills, soft skills, and ideal candidate
   - Enhanced the tailoring process to use the AI analysis for better matching

6. **Provider Support:**
   - Added support for both Claude and OpenAI as analysis providers
   - Implemented configuration settings for provider selection
   - Added fallback logic when using "auto" provider selection
   - Prioritized OpenAI for job analysis when both providers are available

## YC-Eddie Style Implementation Details

1. **YC-Eddie Style Resume Format:**
   - Implement a single, high-quality resume format based on YC and Eddie's best practices
   - Create consistent document styling with professional fonts, spacing, and margins
   - Define structured formatting for headers, section titles, and content
   - Apply uniform bullet point styling and paragraph formatting
   - Ensure ATS compatibility while maintaining professional appearance

2. **Document Generation Enhancements:**
   - Create a completely new document instead of using the original as a template
   - Remove dependency on original document formatting that causes duplicate headers
   - Implement dedicated `resume_styler.py` module for consistent document styling
   - Define precise formatting specifications (fonts, sizes, margins, spacing)
   - Create proper heading hierarchies with consistent styling
   - Standardize bullet point formatting for experience and skills sections

3. **Specific Formatting Requirements:**
   - **Document Properties**:
     - Margins: 1.0cm top/bottom, 2.0cm left/right
     - Default font: Calibri, 11pt
     - Page size: Letter (8.5" x 11")
   - **Section Headers**:
     - Font: Calibri, 14pt, bold
     - Color: Dark blue (RGB: 0, 0, 102)
     - Centered alignment with full box border (all four sides)
     - Spacing: 6pt after header
     - Added spacing before each section
   - **Contact Information**:
     - Font: Calibri, 12pt
     - Alignment: Center
     - Include name, email, phone, and optional LinkedIn/website
   - **Bullet Points**:
     - Indentation: 0.25" left indent, -0.25" first line (hanging indent)
     - Arrow character (▸) instead of standard bullet (•)
     - Spacing: 6pt after each bullet point
     - Consistent formatting across all sections

4. **Implementation Components:**
   - Create `YCEddieStyler` class with methods for:
     - Setting document properties (margins, default styling)
     - Creating and applying section styles (headers, content, bullets)
     - Processing each section with appropriate formatting
     - `add_box_border` method for adding borders to section headers
     - `add_bullet_point` method for consistent arrow-style bullets
   - Modify `generate_tailored_resume_document` to:
     - Create a new blank document instead of using original template
     - Apply YC-Eddie styling through the styler class
     - Add tailored content with consistent section formatting
     - Save with appropriate naming convention

5. **Prompt Optimization (Priority):**
   - Research and document effective resume content patterns from YC and Eddie
   - Enhance system prompts with specific guidance for high-quality resume content
   - Implement section-specific prompts with targeted instructions:
     - **Summary**: Concise, impactful summaries positioning the candidate for the role
     - **Experience**: Achievement-focused content with metrics and strong action verbs
     - **Skills**: Prioritized skills aligned with job requirements
     - **Education/Projects**: Consistent formatting with relevant highlights

6. **Implementation Approach:**
   - Create improved base prompts focusing on:
     - Quantifying achievements with specific metrics
     - Using strong action verbs at the beginning of bullet points
     - Focusing on outcomes and impact rather than responsibilities
     - Removing generic or irrelevant information
     - Highlighting experience relevant to the job requirements
     - Maintaining concise, impactful language throughout
   - Add example formats and phrasings for few-shot learning
   - Implement enhanced document styling in the generation process
   - Test outputs against original content to measure improvements

## PDF Export Implementation Details

1. **PDF Generation Approach:**
   - Implemented WeasyPrint library for high-quality HTML-to-PDF conversion
   - Created dedicated PDF exporter module with configurable options
   - Utilized existing HTML preview as the source for PDF generation
   - Added PDF-specific CSS styling and page settings
   - Implemented proper error handling with fallback to DOCX format

2. **PDF Exporter Implementation:**
   - Created `pdf_exporter.py` module with the `PDFExporter` class
   - Implemented `create_pdf_from_html` helper function for easy integration
   - Added metadata support for title, author, and other PDF properties
   - Configured document properties (margins, page size, headers/footers)
   - Implemented font configuration for consistent text rendering
   - Added detailed logging throughout the PDF generation process

3. **PDF Styling:**
   - Created `pdf_styles.css` with print-specific CSS rules
   - Defined page properties using CSS `@page` rules for margins and size
   - Added page headers and footers with pagination
   - Implemented proper page break handling to prevent awkward section splits
   - Applied consistent typography and spacing for professional appearance
   - Configured bullet point styling and list formatting for clarity

4. **Integration with Tailoring Workflow:**
   - Updated `tailoring_handler.py` to use PDF generation instead of DOCX
   - Implemented error handling with automatic fallback to DOCX if PDF fails
   - Added appropriate file type indicators in API responses
   - Maintained the same filename conventions for consistency
   - Preserved HTML preview functionality alongside PDF generation

5. **Cross-Platform Considerations:**
   - Added support for GTK dependencies on Windows systems
   - Ensured Linux compatibility for deployment on hosting platforms
   - Implemented proper file path handling for different operating systems
   - Added clear error messaging for dependency issues
   - Maintained consistent output across different environments

6. **Benefits of PDF Generation:**
   - Consistent appearance across different devices and platforms
   - Professional formatting with precise control over layout
   - Smaller file sizes compared to DOCX for easier sharing
   - Better print quality with properly defined page settings
   - Improved security with read-only document format
   - ATS compatibility with properly structured content

7. **PDF Formatting Issue Resolution:**
   - **Issue**: Content being incorrectly center-aligned in PDF output for PDF input files
   - **Root Cause**: CSS specificity conflict where `.resume-section:first-child { text-align: center; }` (meant for contact section) was affecting all content in PDF-sourced resumes
   - **Analysis**: When processing PDF files, the HTML structure differs from DOCX files since we can't detect formatting details, causing different CSS inheritance behavior
   - **Solution Implemented**:
     - Added explicit content wrapper classes to all sections (`

# Session-Based Storage Implementation Plan

## Objective
Implement a session-based approach for JSON file storage to support multi-user usage of the application and prevent data contamination between different users' resume tailoring sessions.

## Current Issues
- Non-timestamped JSON files (`experience.json`, `education.json`, etc.) are read by the HTML generator but aren't being correctly created
- Path inconsistency between where files are saved and where they're read from
- Risk of data contamination in multi-user environments: users could see each other's resume data
- Race conditions when multiple users tailor resumes simultaneously
- Security/privacy concerns with shared file access

## Implementation Phases

### Phase 1: Session Management Framework (Priority: High)
1. **Frontend Session Creation**:
   - Generate a unique session ID when a user starts using the application
   - Add JavaScript to create and store session ID in localStorage on page load
   - Pass session ID with all form submissions

2. **Backend Session Handling**:
   - Create a `session_manager.py` module with helper functions
   - Implement functions to validate, sanitize and manage session IDs
   - Create consistent path resolution for session-specific directories

3. **Path Consistency**:
   - Implement a centralized helper function to resolve session paths
   - Ensure all file read/write operations use the correct base path
   - Add path normalization to handle OS-specific path formats

### Phase 2: File Operations Update (Priority: High)
1. **Modify JSON Saving**:
   - Update `save_tailored_content_to_json` to use session directories
   - Include session ID in the path for all saved files
   - Create session directories if they don't exist

2. **Update HTML Generator**:
   - Modify `generate_preview_from_llm_responses` to use session paths
   - Update all file read operations to include session ID
   - Add fallback for backward compatibility with existing files

3. **Update PDF Generator**:
   - Ensure PDF exporter uses same session-specific paths
   - Maintain consistent file output locations

### Phase 3: Session Lifecycle Management (Priority: Medium)
1. **Session Cleanup**:
   - Implement automated cleanup for sessions older than 24 hours
   - Add a scheduled task or route to trigger cleanup
   - Handle cleanup errors gracefully without affecting user experience

2. **Session Validation**:
   - Add validation for session IDs to prevent directory traversal attacks
   - Implement a safeguard against invalid session IDs
   - Create default fallback for missing session IDs

3. **Error Handling**:
   - Add robust error handling for all session-related operations
   - Implement logging specifically for session errors
   - Create user-friendly error messages for session issues

## Technical Implementation Details

### Session ID Generation
```javascript
// Frontend implementation in static/js/app.js
function generateSessionId() {
    const timestamp = Date.now();
    const randomPart = Math.random().toString(36).substring(2, 15);
    return `session_${timestamp}_${randomPart}`;
}

function initSession() {
    if (!localStorage.getItem('resumeAppSessionId')) {
        localStorage.setItem('resumeAppSessionId', generateSessionId());
    }
    return localStorage.getItem('resumeAppSessionId');
}

// Initialize session on page load
document.addEventListener('DOMContentLoaded', initSession);

// Add session ID to form submissions
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'sessionId';
        input.value = localStorage.getItem('resumeAppSessionId');
        this.appendChild(input);
    });
});
```

### Session Manager Implementation
```python
# session_manager.py
import os
import re
import time
import shutil
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def sanitize_session_id(session_id):
    """Sanitize session ID to prevent directory traversal attacks"""
    if not session_id:
        return 'default_session'
        
    # Only allow alphanumeric, underscore, hyphen, and dot
    safe_id = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', session_id)
    
    # Ensure it starts with session_ prefix for consistency
    if not safe_id.startswith('session_'):
        safe_id = f'session_{safe_id}'
        
    return safe_id

def get_session_dir(session_id):
    """Get session-specific directory path"""
    safe_id = sanitize_session_id(session_id)
    
    # Determine base directory (handles both test and production environments)
    if current_app.config.get('TESTING', False):
        base_dir = 'uploads'
    else:
        base_dir = os.path.join('static', 'uploads')
    
    # Create session-specific directory
    session_dir = os.path.join(base_dir, 'api_responses', safe_id)
    os.makedirs(session_dir, exist_ok=True)
    
    return session_dir

def cleanup_old_sessions(max_age_hours=24):
    """Clean up session directories older than specified hours"""
    try:
        # Determine base directory
        if current_app.config.get('TESTING', False):
            base_dir = 'uploads'
        else:
            base_dir = os.path.join('static', 'uploads')
        
        api_responses_dir = os.path.join(base_dir, 'api_responses')
        if not os.path.exists(api_responses_dir):
            return 0
            
        now = time.time()
        count = 0
        
        for session_dir in os.listdir(api_responses_dir):
            path = os.path.join(api_responses_dir, session_dir)
            if os.path.isdir(path) and session_dir.startswith('session_'):
                # Extract timestamp from session ID
                try:
                    created_time = float(session_dir.split('_')[1])
                    if now - created_time > max_age_hours * 3600:  # Convert hours to seconds
                        shutil.rmtree(path)
                        count += 1
                        logger.info(f"Cleaned up session directory: {session_dir}")
                except (IndexError, ValueError):
                    # If timestamp can't be extracted, check directory modification time
                    mtime = os.path.getmtime(path)
                    if now - mtime > max_age_hours * 3600:
                        shutil.rmtree(path)
                        count += 1
                        logger.info(f"Cleaned up session directory by mtime: {session_dir}")
        
        return count
    except Exception as e:
        logger.error(f"Error during session cleanup: {str(e)}")
        return 0
```

### Required Code Changes

1. **Update `tailoring_handler.py` to receive session ID**:
```python
@app.route('/tailor-resume', methods=['POST'])
def tailor_resume():
    # Get session ID from request
    session_id = request.form.get('sessionId', 'default_session')
    
    # Pass session ID to processing functions
    output_filename, output_path, llm_client = tailor_resume_with_llm(
        resume_path,
        job_data,
        api_key,
        provider,
        api_url,
        session_id  # New parameter
    )
```

2. **Update `LLMClient` class to store session ID**:
```python
def __init__(self, api_key, session_id=None):
    self.api_key = api_key
    self.session_id = session_id or 'default_session'
```

3. **Modify `save_tailored_content_to_json` method**:
```python
def save_tailored_content_to_json(self):
    """Save tailored content to session-specific JSON files"""
    try:
        # Get session-specific directory
        from session_manager import get_session_dir
        api_responses_dir = get_session_dir(self.session_id)
        
        # Save each section to a separate JSON file
        sections_saved = 0
        for section_name, content in self.tailored_content.items():
            # Skip empty content
            if not content:
                continue
                
            # Create JSON data structure
            json_data = self._create_json_data(section_name, content)
            
            # Define the output file path
            filepath = os.path.join(api_responses_dir, f"{section_name}.json")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(json_data, str):
                    f.write(json_data)
                else:
                    json.dump(json_data, f, indent=2)
            
            sections_saved += 1
            logger.info(f"Saved {section_name} content to {filepath}")
        
        logger.info(f"Saved {sections_saved} sections to session-specific JSON files")
        return True
    except Exception as e:
        logger.error(f"Error saving tailored content to JSON: {str(e)}")
        return False
```

4. **Update `html_generator.py` to use session paths**:
```python
def generate_preview_from_llm_responses(llm_client) -> str:
    """Generate HTML preview from LLM responses"""
    import os
    import json
    from datetime import datetime
    from session_manager import get_session_dir
    
    # Get session-specific directory
    session_id = getattr(llm_client, 'session_id', 'default_session')
    api_responses_dir = get_session_dir(session_id)
    
    # Rest of function remains the same but uses api_responses_dir
```

## Benefits of Session-Based Approach
- Prevents data contamination between multiple users
- Eliminates race conditions when multiple users tailor resumes simultaneously
- Improves security by isolating user data
- Makes debugging easier by organizing files logically
- Provides foundation for future user account integration
- Enables session history tracking without complex database integration
- Improves cleanup and resource management

## Implementation Schedule
- Phase 1: 2 days
- Phase 2: 2 days
- Phase 3: 1 day
- Testing and refinement: 1 day
- Total estimated time: 6 days

## Risks and Mitigations
- **Risk**: Session ID spoofing
  - **Mitigation**: Validate and sanitize all session IDs

- **Risk**: Disk space issues with many simultaneous users
  - **Mitigation**: Implement regular cleanup of old sessions

- **Risk**: Session persistence across browser restarts
  - **Mitigation**: Use localStorage for persistent session storage

- **Risk**: Path resolution inconsistencies across operating systems
  - **Mitigation**: Use os.path functions consistently for path manipulation

## Success Criteria
- Multiple users can use the system simultaneously without data contamination
- HTML preview reads from the correct session-specific JSON files
- PDF generation uses the same files as the HTML preview
- Old sessions are automatically cleaned up
- File paths are consistent across the application
- No security vulnerabilities introduced by session handling

# Resume Format Enhancement Task

## Objective
Redesign the resume layout to match the specified format below, with company/location on first line and position/dates on second line.

## Current Format
```
<strong>Position</strong> | Company, Location | Dates
```

## Desired Format
```
COMPANY                                        LOCATION
Position                                       Dates
```

## Key Changes Required
1. Company name and location on first line:
   - Company name aligned left
   - Location aligned right

2. Position and dates on second line:
   - Position aligned left
   - Dates aligned right
   
3. Remove all vertical bars ("|") from the formatting

4. Update styling to reflect this new format:
   - Company name in uppercase
   - No bold formatting for the position

## Implementation Steps
1. Modify the HTML/CSS structure to support the new layout
2. Update the `_format_experience_json` method in `claude_integration.py`
3. Test the changes with different resume types
4. Apply similar changes to education and project sections

## Benefits
- Improved readability with clearer hierarchy
- More professional appearance
- Better alignment with industry standard resume formats
- Cleaner visual presentation

## Priority
High - This is a core visual enhancement that affects all generated resumes.

# Code Refactoring Plan

## Objective
Refactor `claude_integration.py` into smaller, more focused modules to improve maintainability, reduce indentation errors, and make the codebase more robust.

## Current Issues
- `claude_integration.py` has grown too large (~2000 lines)
- Multiple indentation errors that are difficult to fix completely
- High coupling between different functionalities
- Difficult to test and maintain
- Mixing of concerns (LLM integration, formatting, parsing, etc.)

## Modularization Strategy
We'll extract functionality into logical groups, creating new modules for each. The approach will be incremental:
1. Extract one functional group at a time
2. Update imports in dependent files
3. Test thoroughly before proceeding to the next group
4. Commit changes after each successful extraction

## Proposed Modules

### 1. `llm_client.py` - LLM Client Base and API Integration
- Base `LLMClient` abstract class
- `ClaudeClient` implementation
- `OpenAIClient` implementation
- Client initialization and API connection code

### 2. `content_formatter.py` - Resume Content Formatting
- `format_section_content`
- `format_experience_content`
- `format_education_content`
- `format_projects_content` 
- `format_job_entry`
- `format_education_entry`
- `format_project_entry`

### 3. `resume_parser.py` - Resume Section Extraction
- `extract_resume_sections`
- `clean_bullet_points`
- `validate_bullet_point_cleaning`

### 4. `html_generator.py` - HTML Generation for Preview and Export
- `validate_html_content`
- `generate_preview_from_llm_responses`
- `generate_resume_preview`

### 5. `resume_tailoring.py` - Core Tailoring Logic
- `tailor_resume_with_llm`

## Implementation Plan

### Phase 1: Extract LLM Client Code
1. Create `llm_client.py` file
2. Move `LLMClient`, `ClaudeClient`, and `OpenAIClient` classes
3. Update imports in dependent files:
   - `tailoring_handler.py`
   - Other files that directly use these classes
4. Test application functionality
5. Commit changes

### Phase 2: Extract Content Formatting Code
1. Create `content_formatter.py` file
2. Move all formatting functions
3. Update imports in dependent files
4. Test application functionality
5. Commit changes

### Phase 3: Extract Resume Parser Code
1. Create `resume_parser.py` file 
2. Move parsing related functions
3. Update imports in dependent files
4. Test application functionality
5. Commit changes

### Phase 4: Extract HTML Generator Code
1. Create `html_generator.py` file
2. Move HTML generation functions
3. Update imports in dependent files
4. Test application functionality
5. Commit changes

### Phase 5: Create Core Tailoring Module
1. Create `resume_tailoring.py`
2. Move core tailoring functions
3. Update imports in all dependent files
4. Perform comprehensive testing
5. Commit changes

### Phase 6: Clean up `claude_integration.py`
1. Convert `claude_integration.py` to a simple facade that imports from new modules
2. Add appropriate deprecation warnings
3. Eventually remove once all dependencies are updated
4. Test application functionality
5. Commit changes

## Testing Approach
After each phase:
1. Start the application
2. Test the resume upload flow
3. Test the job parsing flow
4. Test the resume tailoring flow
5. Verify HTML preview is generated correctly
6. Verify PDF download works properly

## Benefits
- Improved maintainability with smaller, focused files
- Easier debugging and testing
- Reduced likelihood of indentation errors
- Better separation of concerns
- More intuitive codebase organization
- Easier onboarding for new developers

## Debug Plan for HTML Shrinking Issue

### Issue Description
After refactoring `claude_integration.py` into smaller modules including `html_generator.py`, the HTML preview of tailored resumes appears "shrunk" with excessive margins on both sides, creating a narrow column of content instead of utilizing the full width of the preview area.

### Components Involved
1. **Primary Components**:
   - `html_generator.py`: Responsible for generating HTML preview content
   - CSS styles defined within the generated HTML
   - `tailoring_handler.py`: Orchestrates the preview generation process

2. **Secondary Components**:
   - `resume_tailoring.py`: Provides content to the HTML generator
   - `content_formatter.py`: Formats content before HTML generation

### Possible Root Causes

1. **CSS Style Changes**:
   - Max-width constraints might have been added or modified during refactoring
   - Body or container element styles might have changed
   - Missing or modified responsive design elements
   - Container div classes or IDs might have changed without corresponding CSS updates

2. **HTML Structure Changes**:
   - Wrapper element structure might have changed
   - Missing container divs that previously defined the layout
   - Additional nesting levels creating unexpected style inheritance

3. **Style Inheritance Issues**:
   - CSS specificity conflicts after refactoring
   - Missing style reset or base styles
   - Conflicting styles from multiple sources

4. **Refactoring Artifacts**:
   - Incomplete function transfers during refactoring
   - Missed style elements when moving code between files
   - References to outdated class names or IDs

### Debug Steps

1. **Compare Original vs. Refactored Code**:
   ```bash
   # Pull the original file from the main branch
   git show origin/main:claude_integration.py > claude_integration.original.py
   
   # Compare HTML generation functions
   diff -u claude_integration.original.py html_generator.py > html_diff.txt
   ```

2. **Analyze HTML Output**:
   - Generate HTML preview using both original and refactored code
   - Save both HTML outputs to files for comparison
   - Use browser dev tools to inspect CSS differences
   - Identify which CSS rules are causing the narrow display

3. **Inspect CSS in HTML Generator**:
   - Examine the CSS styles defined in `html_generator.py`
   - Focus on styles related to:
     - `body` element
     - Container divs
     - Width, max-width, and margin properties
     - Media queries for responsive design

4. **Verify Template Consistency**:
   - Check if the HTML template structure changed during refactoring
   - Ensure all necessary wrapper elements are present
   - Verify CSS class names match between HTML elements and style definitions

5. **Test CSS Modifications**:
   - Create a test branch for experimentation
   - Systematically modify CSS properties to identify which ones affect layout
   - Test removing max-width constraints
   - Adjust margin and padding settings
   - Test with various screen sizes to verify responsive behavior

### Implementation Plan

1. **Analysis Phase** (Day 1):
   - [ ] Compare original and refactored HTML generation code
   - [ ] Generate and compare HTML outputs
   - [ ] Identify specific CSS rules causing the narrow layout
   - [ ] Document findings in KNOWN_ISSUES.md

2. **Solution Design** (Day 1-2):
   - [ ] Create targeted CSS fixes based on analysis
   - [ ] Test fixes in isolation before integration
   - [ ] Document proposed changes

3. **Implementation** (Day 2):
   - [ ] Apply changes to `html_generator.py`
   - [ ] Test with multiple resume formats and screen sizes
   - [ ] Verify responsive behavior

4. **Verification** (Day 2-3):
   - [ ] Conduct comprehensive testing with various resume types
   - [ ] Check for any other layout issues introduced by changes
   - [ ] Verify that HTML preview matches PDF output layout

5. **Documentation** (Day 3):
   - [ ] Update FILE_DEPENDENCIES.md with any structural changes
   - [ ] Document the fix in KNOWN_ISSUES.md
   - [ ] Create developer notes about the HTML generation process

### Specific Areas to Investigate

1. **CSS Style Blocks**:
   - Look for `<style>` tags in the HTML output
   - Check for properties like `max-width`, `margin`, `width` on container elements
   - Pay attention to `body` styles and top-level containers

2. **Container Structure**:
   - Inspect the HTML structure around `section` elements
   - Look for missing or modified wrapper divs
   - Check class assignments on container elements

3. **Media Queries**:
   - Verify if responsive design elements are intact
   - Check if media query breakpoints match between versions

4. **Common Layout Patterns**:
   - Look for standard layout patterns like:
     - Centered content with max-width
     - Flexbox or Grid containers
     - Responsive adjustments

### Success Criteria
- HTML preview utilizes appropriate width (similar to original implementation)
- Content is properly displayed without excessive margins
- Layout is responsive to different screen sizes
- PDF output matches the HTML preview layout