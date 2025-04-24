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
- [x] Fix Python module import path issue by adding current directory to sys.path in app.py
- [x] Fix missing contact section in tailored resume
- [x] Fix missing professional summary section in tailored resume

## In Progress Tasks

- [x] Switch from Word document generation to PDF export for better consistency
- [x] Implement HTML-to-PDF conversion with professional styling
- [x] Update download functionality to provide PDF files instead of Word documents
- [x] Optimize PDF layout for ATS compatibility and professional appearance
- [ ] Optimize tailoring prompts for high-quality, achievement-focused content
- [ ] Create resume format validator to help prepare optimal resumes
- [ ] Add visual diff feature to highlight tailoring changes
- [ ] Add confidence scores to LLM parsing results

## Future Tasks

- [ ] Implement alternative LLM providers as fallback options
- [ ] Add job search functionality using search engine tools
- [ ] Create user accounts and save tailoring history
- [ ] Implement resume scoring against job requirements
- [ ] Add bulk processing of multiple job listings
- [ ] Implement few-shot learning with example resumes for improved parsing
- [ ] Add section-specific prompts for more accurate tailoring

## New Tasks

- [x] Fix missing contact section in tailored resume
  - Ensure contact information is preserved during the tailoring process.
  - Improve caching mechanisms for parsed resume data.
  - Add a fallback mechanism to extract contact information directly from the original document.
  - Update the LLM prompt to explicitly extract and preserve contact information.
  - **Priority**: Critical
  - **Implemented**: Added contact section preservation in tailor_resume_with_llm, improved error handling in html_generator.py, and enhanced validation in save_tailored_content_to_json.

- [x] Fix missing professional summary section
  - Ensure the summary section is included in the LLM parsing and tailoring process.
  - Add validation to check for the presence of a summary section.
  - Update the approach by preserving the original summary instead of tailoring it.
  - Add a fallback mechanism to extract summary information from the original parsed resume.
  - **Priority**: High
  - **Implemented**: Added summary section preservation in tailor_resume_with_llm similar to the contact section approach, added validation in save_tailored_content_to_json, and implemented a fallback mechanism in html_generator.py.

- [ ] Adjust resume formatting to utilize full A4 page width
  - Adjust the HTML/CSS styling to utilize the full A4 page width.
  - Review and update the PDF generation settings to ensure proper page width.
  - **Priority**: Medium

- [ ] Remove frame lines in PDF download
  - Review and adjust the CSS styling to remove unwanted frame lines.
  - Ensure the PDF generation process does not include unnecessary borders.
  - **Priority**: Medium

## Task Breakdown: Fix Missing Professional Summary Section

### Issue Analysis
The professional summary section is missing from the tailored resume output, similar to the previous contact section issue. After analyzing the code:

1. In `claude_integration.py`, the `tailor_resume_with_llm` function was treating the summary section as a section to be tailored:
```python
for section_name, content in resume_sections.items():
    if content.strip() and section_name in ["summary", "experience", "education", "skills", "projects"]:
        logger.info(f"Tailoring {section_name} section")
        tailored_content = llm_client.tailor_resume_content(section_name, content, job_data)
        resume_sections[section_name] = tailored_content
```

2. However, the summary is a critical section that should be preserved in its original form, similar to the contact section.

3. The HTML generator was looking for a `summary.json` file in the API responses directory, but it was either not being created or had a different structure than expected.

### Root Cause
The summary section was being treated as a section to be tailored by the LLM, but in many cases, the LLM might not generate a tailored summary, resulting in the section being missing from the final resume.

### Implemented Fix

1. **Modified the `tailor_resume_with_llm` function in `claude_integration.py`**:
   - Added the summary section directly to the LLM client's `tailored_content` dictionary without tailoring it:
```python
# Add summary section directly to tailored_content without tailoring it
if resume_sections.get("summary", "").strip():
    logger.info(f"Preserving summary section for tailored resume: {len(resume_sections['summary'])} chars")
    llm_client.tailored_content["summary"] = resume_sections["summary"]
else:
    logger.warning("No summary information found in resume sections")
```

2. **Enhanced validation in `save_tailored_content_to_json`**:
   - Added validation to check for the presence of the summary section:
```python
# Validate that summary section exists
if "summary" not in sections_available:
    logger.warning("Summary section not found in tailored content. This will result in missing professional summary in the resume.")
```
   - Added verification to confirm that the summary.json file was created:
```python
# Verify summary.json was created
summary_path = os.path.join(api_responses_dir, "summary.json")
if os.path.exists(summary_path):
    logger.info(f"Verified summary.json exists at {summary_path}")
else:
    logger.warning(f"Summary.json was not created at {summary_path}")
```

3. **Added a fallback mechanism in `html_generator.py`**:
   - Implemented a fallback method to retrieve the summary from the original resume parsing if the summary.json file isn't found:
```python
# Fallback: Try to get summary info from the original resume parsing
try:
    # Get the resume file ID from the current context
    from flask import current_app, g
    if hasattr(g, 'resume_file_id') and g.resume_file_id:
        resume_id = g.resume_file_id
        logger.info(f"Attempting to recover summary from original resume parsing (ID: {resume_id})")
        
        # Try to locate the cached parsing result
        import glob
        llm_parsed_files = glob.glob(os.path.join(current_app.config['UPLOAD_FOLDER'], f"*{resume_id}*_llm_parsed.json"))
        
        if llm_parsed_files:
            with open(llm_parsed_files[0], 'r') as f:
                cached_data = json.load(f)
                if cached_data.get('sections') and cached_data['sections'].get('summary'):
                    summary_text = cached_data['sections'].get('summary', '')
                    # Add summary section to HTML output
```

### Expected Results
The fix should successfully:
1. Preserve the original summary section without trying to tailor it
2. Provide proper validation and verification for the summary.json file
3. Implement a fallback mechanism to recover the summary from cached parsing results if needed
4. Display the professional summary section correctly in the tailored resume output

### Next Steps
With the summary section fix complete, the next issues to address are:
1. Adjust resume formatting to utilize full A4 page width
2. Remove frame lines in PDF download
3. Address other remaining formatting issues in KNOWN_ISSUES.md

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
</rewritten_file> 